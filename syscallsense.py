"""
SysCallSense: Lightweight Transformer-Based HIDS on ADFA-LD
-----------------------------------------------------------
Run:
    python syscallsense.py

Requires:
    pip install torch numpy scikit-learn matplotlib requests
    
Dataset: ADFA-LD (downloaded automatically from GitHub mirror)
"""

import os
import re
import math
import random
import zipfile
import urllib.request
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, roc_auc_score
import matplotlib.pyplot as plt

# ── reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ── hyper-parameters ─────────────────────────────────────────────────────────
WINDOW      = 50        # sliding window length
STRIDE      = 10        # window stride
D_MODEL     = 128       # transformer hidden dim
N_HEADS     = 4         # attention heads
N_LAYERS    = 4         # transformer layers
DROPOUT     = 0.1
BATCH       = 64
EPOCHS      = 10
LR          = 1e-3
PPL_PCTILE  = 95        # threshold = 95th pctile of normal val perplexity
DATA_DIR    = "adfa_ld"

# ── 1. DOWNLOAD & PARSE ADFA-LD ──────────────────────────────────────────────

ADFA_URL = (
    "https://github.com/verazuo/a-labelled-version-of-the-ADFA-LD-dataset/blob/master/ADFA-LD.zip"
)

def download_adfa():
    # if os.path.isdir(DATA_DIR):
    #     print("[data] ADFA-LD already extracted.")
    #     return
    zip_path = "adfa_ld2.zip"
    # if not os.path.isfile(zip_path):
    #     print("[data] Downloading ADFA-LD …")
    #     urllib.request.urlretrieve(ADFA_URL, zip_path)
    # print("[data] Extracting …")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(".")
    # rename extracted folder
    extracted = [d for d in os.listdir(".") if d.startswith("adfa-ld")]
    if extracted:
        os.rename(extracted[0], DATA_DIR)
    print("[data] Done.")


def read_traces(folder):
    """Return list of token-ID sequences from a folder of syscall trace files."""
    traces = []
    if not os.path.isdir(folder):
        return traces
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            with open(fpath, "r", errors="ignore") as f:
                tokens = f.read().split()
            traces.append(tokens)
    return traces


def build_vocab(traces):
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for tr in traces:
        for t in tr:
            if t not in vocab:
                vocab[t] = len(vocab)
    return vocab


def encode(traces, vocab):
    unk = vocab["<UNK>"]
    return [[vocab.get(t, unk) for t in tr] for tr in traces]


def make_windows(encoded_traces, window=WINDOW, stride=STRIDE):
    """Slice each trace into overlapping windows; label = 0 (next-token target)."""
    inputs, targets = [], []
    for tr in encoded_traces:
        for start in range(0, len(tr) - window, stride):
            seg = tr[start: start + window + 1]
            if len(seg) < window + 1:
                continue
            inputs.append(seg[:window])
            targets.append(seg[1: window + 1])
    return inputs, targets


# ── 2. DATASET ────────────────────────────────────────────────────────────────

class SyscallDataset(Dataset):
    def __init__(self, inputs, targets):
        self.x = torch.tensor(inputs, dtype=torch.long)
        self.y = torch.tensor(targets, dtype=torch.long)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


# ── 3. LIGHTWEIGHT SPARSE-ATTENTION TRANSFORMER ───────────────────────────────

class SparseAttention(nn.Module):
    """Local-window multi-head attention (sparse approximation)."""
    def __init__(self, d_model, n_heads, local_window=32):
        super().__init__()
        self.n_heads   = n_heads
        self.d_k       = d_model // n_heads
        self.local_w   = local_window
        self.q_proj    = nn.Linear(d_model, d_model)
        self.k_proj    = nn.Linear(d_model, d_model)
        self.v_proj    = nn.Linear(d_model, d_model)
        self.out_proj  = nn.Linear(d_model, d_model)

    def forward(self, x):
        B, T, _ = x.shape
        Q = self.q_proj(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        K = self.k_proj(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        V = self.v_proj(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)

        # build causal + local-window mask  (B, 1, T, T)
        mask = torch.full((T, T), float("-inf"), device=x.device)
        for i in range(T):
            lo = max(0, i - self.local_w)
            mask[i, lo:i + 1] = 0.0          # causal local window
        mask = mask.unsqueeze(0).unsqueeze(0)  # (1,1,T,T)

        scores = (Q @ K.transpose(-2, -1)) / math.sqrt(self.d_k) + mask
        attn   = torch.softmax(scores, dim=-1)
        out    = (attn @ V).transpose(1, 2).contiguous().view(B, T, -1)
        return self.out_proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, dropout):
        super().__init__()
        self.attn  = SparseAttention(d_model, n_heads)
        self.ff    = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Linear(d_model * 4, d_model),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop  = nn.Dropout(dropout)

    def forward(self, x):
        x = x + self.drop(self.attn(self.norm1(x)))
        x = x + self.drop(self.ff(self.norm2(x)))
        return x


class SysCallTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=D_MODEL, n_heads=N_HEADS,
                 n_layers=N_LAYERS, max_len=WINDOW, dropout=DROPOUT):
        super().__init__()
        self.embed   = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_enc = nn.Embedding(max_len, d_model)
        self.layers  = nn.ModuleList(
            [TransformerBlock(d_model, n_heads, dropout) for _ in range(n_layers)]
        )
        self.norm    = nn.LayerNorm(d_model)
        self.head    = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        B, T = x.shape
        pos  = torch.arange(T, device=x.device).unsqueeze(0)
        h    = self.embed(x) + self.pos_enc(pos)
        for layer in self.layers:
            h = layer(h)
        return self.head(self.norm(h))   # (B, T, vocab_size)


# ── 4. TRAINING ───────────────────────────────────────────────────────────────

def train_epoch(model, loader, optimiser, criterion, device):
    model.train()
    total_loss = 0.0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb)                          # (B, T, V)
        loss   = criterion(logits.view(-1, logits.size(-1)), yb.view(-1))
        optimiser.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimiser.step()
        total_loss += loss.item()
    return total_loss / len(loader)


# ── 5. PERPLEXITY SCORING ─────────────────────────────────────────────────────

@torch.no_grad()
def perplexity_scores(model, encoded_traces, vocab_size, device,
                      window=WINDOW, stride=STRIDE):
    """Return per-trace mean perplexity."""
    model.eval()
    criterion = nn.CrossEntropyLoss(reduction="mean")
    ppls = []
    for tr in encoded_traces:
        wins = []
        for start in range(0, len(tr) - window, stride):
            seg = tr[start: start + window + 1]
            if len(seg) < window + 1:
                continue
            wins.append(seg)
        if not wins:
            ppls.append(float("nan"))
            continue
        xb = torch.tensor([w[:window] for w in wins], dtype=torch.long, device=device)
        yb = torch.tensor([w[1:window+1] for w in wins], dtype=torch.long, device=device)
        logits = model(xb)
        loss   = criterion(logits.view(-1, vocab_size), yb.view(-1))
        ppls.append(math.exp(loss.item()))
    return ppls


# ── 6. EVALUATION ─────────────────────────────────────────────────────────────

def evaluate(normal_ppls, attack_ppls, threshold):
    y_true, y_score = [], []
    for p in normal_ppls:
        if not math.isnan(p):
            y_true.append(0)
            y_score.append(p)
    for p in attack_ppls:
        if not math.isnan(p):
            y_true.append(1)
            y_score.append(p)

    y_pred = [1 if s > threshold else 0 for s in y_score]
    print("\n── Classification Report ────────────────────────────")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Attack"],
                                 zero_division=0))
    try:
        auc = roc_auc_score(y_true, y_score)
        print(f"AUC-ROC : {auc:.4f}")
    except Exception:
        pass
    tp = sum(p == 1 and t == 1 for p, t in zip(y_pred, y_true))
    tn = sum(p == 0 and t == 0 for p, t in zip(y_pred, y_true))
    fp = sum(p == 1 and t == 0 for p, t in zip(y_pred, y_true))
    fn = sum(p == 0 and t == 1 for p, t in zip(y_pred, y_true))
    tpr = tp / (tp + fn + 1e-9)
    tnr = tn / (tn + fp + 1e-9)
    print(f"TPR (Recall)  : {tpr:.4f}")
    print(f"TNR (Specif.) : {tnr:.4f}")
    return tpr, tnr, y_true, y_score


def plot_ppls(normal_ppls, attack_ppls, threshold, save_path="ppl_distribution.png"):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist([p for p in normal_ppls if not math.isnan(p)], bins=40,
            alpha=0.6, label="Normal", color="steelblue")
    ax.hist([p for p in attack_ppls if not math.isnan(p)], bins=40,
            alpha=0.6, label="Attack", color="tomato")
    ax.axvline(threshold, color="black", linestyle="--", label=f"Threshold={threshold:.1f}")
    ax.set_xlabel("Perplexity")
    ax.set_ylabel("Count")
    ax.set_title("SysCallSense – Perplexity Distribution (Normal vs. Attack)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"[plot] Saved to {save_path}")


# ── 7. MAIN ───────────────────────────────────────────────────────────────────

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[device] {device}")

    # ── download dataset ──
    download_adfa()

    # ── locate folders ──
    # ADFA-LD folder structure:
    #   adfa_ld/ADFA-LD/Training_Data_Master/
    #   adfa_ld/ADFA-LD/Attack_Data_Master/<attack>/
    base = DATA_DIR
    # try to find Training and Attack directories
    train_dir, attack_root = None, None
    for root, dirs, _ in os.walk(base):
        for d in dirs:
            if "Training_Data_Master" in d:
                train_dir = os.path.join(root, d)
            if "Attack_Data_Master" in d:
                attack_root = os.path.join(root, d)

    if train_dir is None or attack_root is None:
        # Fallback: generate synthetic traces for demonstration
        print("[data] ADFA-LD folder structure not found — generating synthetic data.")
        vocab_synth = {str(i): i + 2 for i in range(1, 175)}
        vocab_synth["<PAD>"] = 0
        vocab_synth["<UNK>"] = 1
        rng = np.random.default_rng(SEED)
        normal_traces_enc = [rng.integers(2, 176, size=200).tolist() for _ in range(400)]
        # attacks: inject unusual tokens
        attack_traces_enc = []
        for _ in range(100):
            tr = rng.integers(2, 176, size=200).tolist()
            # inject rare sequence at random position
            pos = rng.integers(0, 150)
            tr[pos:pos+5] = rng.integers(176, 200, size=5).tolist()
            attack_traces_enc.append(tr)
        vocab = vocab_synth
    else:
        print(f"[data] Training dir : {train_dir}")
        print(f"[data] Attack root  : {attack_root}")

        # read normal traces
        normal_traces_raw = read_traces(train_dir)
        print(f"[data] Normal traces : {len(normal_traces_raw)}")

        # read attack traces (all subfolders)
        attack_traces_raw = []
        for sub in os.listdir(attack_root):
            sub_path = os.path.join(attack_root, sub)
            if os.path.isdir(sub_path):
                traces = read_traces(sub_path)
                attack_traces_raw.extend(traces)
        print(f"[data] Attack traces : {len(attack_traces_raw)}")

        # build vocab on normal traces only
        vocab = build_vocab(normal_traces_raw)
        print(f"[data] Vocabulary size : {len(vocab)}")

        normal_traces_enc = encode(normal_traces_raw, vocab)
        attack_traces_enc = encode(attack_traces_raw, vocab)

    vocab_size = max(vocab.values()) + 1 if isinstance(list(vocab.values())[0], int) else len(vocab) + 2

    # ── train / val split ──
    random.shuffle(normal_traces_enc)
    split       = int(0.8 * len(normal_traces_enc))
    train_enc   = normal_traces_enc[:split]
    val_enc     = normal_traces_enc[split:]

    print(f"\n[split] Train={len(train_enc)}  Val={len(val_enc)}  Attack={len(attack_traces_enc)}")

    # ── build windowed dataset ──
    tr_inputs, tr_targets = make_windows(train_enc)
    print(f"[windows] Training windows : {len(tr_inputs)}")

    train_ds     = SyscallDataset(tr_inputs, tr_targets)
    train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True,
                              num_workers=0, pin_memory=False)

    # ── model ──
    model     = SysCallTransformer(vocab_size).to(device)
    n_params  = sum(p.numel() for p in model.parameters())
    print(f"[model] Parameters : {n_params:,}")

    optimiser = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=EPOCHS)

    # ── training loop ──
    print("\n── Training ─────────────────────────────────────────")
    losses = []
    for epoch in range(1, EPOCHS + 1):
        loss = train_epoch(model, train_loader, optimiser, criterion, device)
        scheduler.step()
        losses.append(loss)
        print(f"Epoch {epoch:02d}/{EPOCHS}  loss={loss:.4f}")

    # ── calibrate threshold on validation normals ──
    print("\n── Calibrating threshold on validation normals …")
    val_ppls    = perplexity_scores(model, val_enc, vocab_size, device)
    val_ppls_ok = [p for p in val_ppls if not math.isnan(p)]
    threshold   = float(np.percentile(val_ppls_ok, PPL_PCTILE))
    print(f"[threshold] {PPL_PCTILE}th percentile = {threshold:.2f}")

    # ── score attack traces ──
    print("── Scoring attack traces …")
    attack_ppls = perplexity_scores(model, attack_traces_enc, vocab_size, device)

    # ── evaluate ──
    tpr, tnr, y_true, y_score = evaluate(val_ppls_ok,
                                          [p for p in attack_ppls if not math.isnan(p)],
                                          threshold)

    # ── plot ──
    plot_ppls(val_ppls_ok,
              [p for p in attack_ppls if not math.isnan(p)],
              threshold)

    # ── save model ──
    torch.save(model.state_dict(), "syscallsense_model.pt")
    print("\n[saved] syscallsense_model.pt")
    print("\n── Done ─────────────────────────────────────────────")


# ── BONUS: LLM explanation stub ───────────────────────────────────────────────

def explain_anomaly(syscall_window: list, perplexity: float) -> dict:
    """
    Calls Anthropic Claude to generate a plain-language explanation.
    Replace ANTHROPIC_API_KEY with your key, or set as env variable.
    
    In production, this runs server-side; on a local PC it can call
    a small local LLM (e.g., llama.cpp) instead.
    """
    import json, os
    # Stub response for demonstration (avoids requiring API key at test time)
    stub = {
        "summary": (
            f"An unusual system call sequence was detected "
            f"(perplexity={perplexity:.1f}). "
            f"The sequence '{' '.join(str(s) for s in syscall_window[:5])} …' "
            f"deviates significantly from normal baseline behaviour."
        ),
        "likely_cause": (
            "Possible unauthorized file manipulation or privilege escalation attempt. "
            "A malware payload performing reconnaissance or data exfiltration "
            "could produce this pattern."
        ),
        "recommended_action": (
            "1. Note the process ID and check running processes. "
            "2. Scan the system with your antivirus tool. "
            "3. If suspicious, isolate the machine from the network."
        ),
    }
    return stub


if __name__ == "__main__":
    main()

    # Demonstrate explanation module
    print("\n── LLM Explanation Demo ─────────────────────────────")
    sample_window = [42, 17, 99, 5, 112, 8, 7, 42, 99, 5]
    sample_ppl    = 312.4
    explanation   = explain_anomaly(sample_window, sample_ppl)
    for k, v in explanation.items():
        print(f"\n[{k.upper()}]\n{v}")
