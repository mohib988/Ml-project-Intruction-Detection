import pandas as pd
import numpy as np
from pathlib import Path

# Load one attack file the same way as LSTM notebook
csv_file = Path('Dataset/DDoS_HTTP_Flood_attack.csv')
df = pd.read_csv(csv_file, nrows=100)

print(f"Original shape: {df.shape}")
print(f"Original columns: {df.columns.tolist()}\n")

# Apply same cleaning as LSTM notebook
df = df.drop_duplicates(keep='first')

drop_columns = [
    'ip.src_host', 'arp.src.proto_ipv4', 'arp.dst.proto_ipv4',
    'http.file_data', 'http.request.full_uri', 'icmp.transmit_timestamp',
    'http.request.uri.query', 'tcp.options', 'tcp.payload',
    'mqtt.msg', 'http.referer', 'http.request.version', 
    'tcp.srcport', 'dns.qry.name', 'mqtt.topic', 'mqtt.protoname'
]
drop_cols = [col for col in drop_columns if col in df.columns]
df = df.drop(columns=drop_cols, errors='ignore')

print(f"After dropping columns: {df.shape}")

# Convert numeric cols
numeric_cols = [
    'icmp.seq_le', 'tcp.ack_raw', 'tcp.connection.fin', 'tcp.len',
    'tcp.dstport', 'arp.hw.size', 'udp.port', 'mqtt.conack.flags',
    'mqtt.conflags', 'mqtt.hdrflags', 'tcp.flags', 'icmp.checksum', 'tcp.checksum'
]

def convert_mixed(val):
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("0x"):
            try:
                return int(val, 16)
            except:
                return np.nan
        return pd.to_numeric(val, errors='coerce')
    return val

for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].apply(convert_mixed)

# Remove single-value columns
single_val = []
for col in df.columns:
    if df[col].nunique() == 1 and col not in ['Attack_type', 'Attack_label']:
        single_val.append(col)
df = df.drop(columns=single_val, errors='ignore')

print(f"After removing single-value columns: {df.shape}")

# Parse datetime
if 'frame.time' in df.columns:
    df['frame.time'] = pd.to_datetime(df['frame.time'], errors='coerce')

# One-hot encode
cat_cols = df.select_dtypes(include=['object']).columns.tolist()
exclude = {'frame.time', 'ip.dst_host', 'Attack_type', 'Attack_label'}
cat_cols = [col for col in cat_cols if col not in exclude]

print(f"\nCategorical columns to encode: {cat_cols}\n")

for col in cat_cols:
    try:
        dummies = pd.get_dummies(df[col], prefix=col, dummy_na=False)
        df = pd.concat([df, dummies], axis=1)
        df = df.drop(col, axis=1)
        print(f"  Encoded {col} -> {dummies.shape[1]} columns")
    except Exception as e:
        print(f"  Error encoding {col}: {e}")

print(f"\nFinal shape: {df.shape}")

# Extract feature columns (same as notebook)
exclude_cols = {'frame.time', 'ip.dst_host', 'Attack_type', 'Attack_label'}
feature_cols = [col for col in df.columns if col not in exclude_cols]

print(f"\nFeature columns: {len(feature_cols)}")
print(f"Feature list:")
for f in feature_cols:
    print(f"  {f}")
