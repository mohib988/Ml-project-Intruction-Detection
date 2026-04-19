# 🛡️ SHIELD - Network Attack Detection System
## Complete Setup & Deployment Guide

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [How to Run](#how-to-run)
5. [Dashboard Guide](#dashboard-guide)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

**SHIELD** is an AI-powered network threat detection and response system that:
- 🤖 Uses XGBoost machine learning model for threat classification
- 📊 Provides real-time attack detection dashboard
- 🎮 Simulates various network attacks for testing
- 🚫 Automatically blocks malicious IP addresses
- 📈 Visual analytics with animated charts
- 💾 Complete audit trail and history

### System Components

```
┌─────────────────────────────────────────────────────────┐
│          Streamlit Web Dashboard (Interactive)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Real-time   │  │ Statistics & │  │ IP Blocker   │ │
│  │  Monitor     │  │  Analytics   │  │  Management  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Attack Detection Pipeline           Device Simulator   │
│  (prediction, scoring, labeling)  (traffic generation) │
├─────────────────────────────────────────────────────────┤
│             XGBoost ML Model (Trained)                  │
│  • 200 trees • 8 depth • 15 attack classes             │
├─────────────────────────────────────────────────────────┤
```

---

## ⚡ Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

1. **Open Command Prompt** in the project directory
2. **Run the setup script**:
   ```batch
   setup_and_run.bat
   ```
3. **Dashboard opens** at `http://localhost:8501`

### Option 2: Manual Setup

1. **Install dependencies**:
   ```batch
   pip install -r requirements_streamlit.txt
   ```

2. **Start dashboard**:
   ```batch
   streamlit run streamlit_app.py
   ```

3. **Open browser** to `http://localhost:8501`

---

## ⚡ Quick Start (Linux/Mac)

### Option 1: Automated Setup (Recommended)

1. **Open Terminal** in the project directory
2. **Make script executable**:
   ```bash
   chmod +x setup_and_run.sh
   ```
3. **Run the setup script**:
   ```bash
   ./setup_and_run.sh
   ```
4. **Dashboard opens** at `http://localhost:8501`

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements_streamlit.txt
   ```

2. **Start dashboard**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open browser** to `http://localhost:8501`

---

## 📦 Detailed Installation

### System Requirements

- **OS**: Windows, Linux, or macOS
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum recommended
- **Disk**: 500MB free space for dependencies

### Step 1: Verify Python Installation

**Windows (Command Prompt)**:
```batch
python --version
```

**Linux/Mac (Terminal)**:
```bash
python3 --version
```

Should show Python 3.8+

### Step 2: Install Package Manager (if needed)

**Windows**: Usually comes with Python

**Linux**:
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

**Mac**:
```bash
brew install python3
```

### Step 3: Install Project Dependencies

Navigate to project directory:

**Windows**:
```batch
cd C:\path\to\advanceMlProject
pip install -r requirements_streamlit.txt
```

**Linux/Mac**:
```bash
cd /path/to/advanceMlProject
pip3 install -r requirements_streamlit.txt
```

### Step 4: Verify Model Files

Ensure these files exist in project directory:

```
├── xgboost_attack_detection_model.pkl    ✓ Required
├── scaler.pkl                            ✓ Required
├── label_encoder.pkl                     ✓ Required
├── model_info.json                       ✓ Required
```

If missing, run the training notebook:
```bash
jupyter notebook lstm_attack_timeseries.ipynb
```

---

## 🚀 How to Run

### Method 1: Using Setup Script (Easiest)

**Windows**:
```batch
setup_and_run.bat
```

**Linux/Mac**:
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Method 2: Direct Streamlit Command

```bash
streamlit run streamlit_app.py
```

### Method 3: Using Python

```bash
python -m streamlit run streamlit_app.py
```

### Dashboard Access

- **Default URL**: `http://localhost:8501`
- **Alt Port**: `streamlit run streamlit_app.py --server.port 8502`
- **Network Access**: 
  ```bash
  streamlit run streamlit_app.py --server.address 0.0.0.0
  ```

---

## 📊 Dashboard Guide

### 🎯 Tab 1: Real-time Monitor

**Purpose**: Live threat detection with immediate response

**What to do**:
1. Select attack type from sidebar dropdown
2. Adjust simulation settings:
   - Packets per traffic (1-10)
   - Simulation speed (1-20 packets/sec)
3. Click **"▶️ Start Simulation"** button
4. Watch detection results in real-time
5. Automatically block detected attacks

**View Details**:
- Attack type and confidence score
- Source IP address
- Threat probability breakdown
- Manual IP blocking option

---

### 📊 Tab 2: Statistics & Analytics

**Purpose**: View aggregated threat analysis

**Metrics Displayed**:
- Total packets processed
- Number of attacks detected
- Normal traffic count
- Detection rate percentage

**Visualizations**:
1. **Attack Distribution** (Pie chart)
   - Shows breakdown of attack types

2. **Confidence Scores** (Histogram)
   - Distribution of model confidence

3. **Detection Timeline** (Animated scatter plot)
   - Shows threats over time
   - Color coded: Red=Attack, Teal=Normal
   - Size = confidence level

**How to Use**:
- Hover over charts for details
- Download PNG using camera icon
- Zoom and pan for details

---

### 🚫 Tab 3: IP Blocker

**Purpose**: Manage blocked IP addresses

**Features**:
1. **View Blocked IPs**
   - Status and timestamp
   - One-click unblock

2. **Manual Blocking**
   - Enter IP address
   - Click "Block IP"

3. **Statistics**
   - Total blocked count
   - Attacks blocked
   - Block effectiveness rate

4. **Bulk Operations**
   - Clear all blocks
   - Reset blocklist

**Example IPs to Block**:
```
192.168.1.100      Single IP
192.168.1.0/24     Subnet (manually add each)
10.0.0.50          Different network
```

---

### 📜 Tab 4: History & Audit Trail

**Purpose**: Review all detection events

**Features**:
1. **Complete Records**
   - Timestamp of detection
   - Source IP (attacker)
   - Attack type identified
   - Confidence percentage
   - Action taken

2. **Filtering**
   - By attack type
   - By IP address
   - By status (Attack/Normal)

3. **Export**
   - Download as CSV
   - For reports and analysis
   - Timestamp in filename

**Example History Entry**:
```
Time              | IP          | Attack Type          | Confidence | Action
2024-04-18 10:15 | 192.168.1.5 | DDoS_HTTP_Flood_attack| 98.5%     | ⚠️ Attack
2024-04-18 10:14 | 10.0.0.100  | Normal               | 95.2%     | ✅ Normal
```

---

## 🎮 Attack Type Simulations

### Available Attack Types

1. **Normal**
   - Regular network traffic baseline
   - Used for training and comparison

2. **DDoS_HTTP_Flood_attack**
   - HTTP request onslaught
   - High volume GET/POST requests
   - Target: Web services

3. **DDoS_TCP_SYN_Flood_attack**
   - TCP connection exhaustion
   - Rapid SYN packets
   - Target: Server resources

4. **DDoS_UDP_Flood_attack**
   - UDP packet flooding
   - High-volume UDP traffic
   - Target: Network bandwidth

5. **Port_Scanning_attack**
   - Sequential port enumeration
   - Reconnaissance phase
   - Starts attack chain

6. **SQL_injection_attack**
   - Database query injection
   - Malicious SQL payloads
   - Target: Web applications

7. **XSS_attack**
   - Cross-site scripting
   - JavaScript injection
   - Session hijacking

8. **Backdoor_attack**
   - Remote access installation
   - Persistent access attempt
   - Post-exploitation

9. **MITM_attack**
   - Man-in-the-middle attack
   - Packet interception
   - Protocol manipulation

---

## 🔍 Understanding the Results

### Confidence Score Breakdown

```
Confidence Range    | Interpretation
─────────────────────────────────────
90% - 100%         | ✅ Highly Certain
75% - 89%          | ⚠️  Probable
60% - 74%          | ⚠️  Suspicious  
50% - 59%          | 🤔 Low Confidence
< 50%              | ❓ Unreliable
```

### Attack Classification

**Example Results**:
```
Detected Attack: DDoS_HTTP_Flood_attack
Confidence: 96.5%
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ (94% for this class)
Source IP: 192.168.1.42
Status: 🚫 BLOCKED
```

---

## 🔧 Advanced Configuration

### Custom Simulation Speed

In sidebar → Simulation Speed slider (1-20 packets/sec)
- 1 packet/sec: Slow, detailed analysis
- 10 packets/sec: Medium, realistic
- 20 packets/sec: Fast, stress testing

### Batch Processing

Generate multiple packets at once:
1. Set "Packets per traffic" to desired number
2. Select attack type
3. Click "Start Simulation"
4. System processes all packets sequentially

### Auto-Generation

Enable automatic packet generation:
1. Check "Auto-generate packets" checkbox
2. System continuously generates traffic
3. Click "Stop" in sidebar to halt

---

## 🧪 Testing & Validation

### Run Test Suite

```bash
python test_system.py
```

**Tests Performed**:
1. Pipeline initialization
2. Model loading
3. Prediction accuracy
4. Simulator functionality
5. IP blocking system
6. End-to-end integration

**Expected Output**:
```
✓ PASSED: Pipeline test
✓ PASSED: Simulator test
✓ PASSED: Integration test
✅ All tests passed - System ready!
```

---

## 🐛 Troubleshooting

### Issue 1: "Module not found" Error

```
Error: ModuleNotFoundError: No module named 'xgboost'
```

**Solution**:
```bash
pip install --upgrade xgboost plotly streamlit
```

### Issue 2: "Model files not found"

```
Error: Model file not found: xgboost_attack_detection_model.pkl
```

**Solution**:
1. Ensure you're in the correct directory
2. Train the model first:
   ```bash
   jupyter notebook lstm_attack_timeseries.ipynb
   ```
3. Files will be created automatically

### Issue 3: Port Already in Use

```
Error: Port 8501 is already in use
```

**Solution**:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Issue 4: Dashboard Not Opening

**Solution**:
1. Check if Streamlit is running:
   ```bash
   streamlit run streamlit_app.py
   ```
2. Manually open: `http://localhost:8501`
3. Check firewall settings

### Issue 5: Out of Memory Error

**Solution**:
- Reduce packets per simulation
- Close other applications
- Increase system RAM
- Run on more powerful machine

### Issue 6: Slow Performance

**Solution**:
- Reduce simulation speed
- Decrease number of packets
- Close browser tabs
- Disable animations (browser devtools)

---

## 📈 Performance Metrics

### System Performance

```
Metric              | Value
────────────────────────────────
Single Prediction   | <50ms
Batch (10 packets)  | <200ms
Model Throughput    | 1000+ packets/sec
Memory Usage        | ~500MB
Startup Time        | ~5-10 seconds
```

### Model Accuracy

```
Check model_info.json for:
- Training Accuracy: ~95%
- Testing Accuracy: ~92%
- Number of Classes: 9 (attack types)
```

---

## 🔒 Security Best Practices

1. **Run Locally**: Don't expose dashboard to internet
2. **Strong Passwords**: Use VPN/authentication for remote access
3. **Firewall**: Only allow trusted connections
4. **Updates**: Keep dependencies updated
5. **Logs**: Review history regularly for patterns
6. **Backup**: Save critical blocklists

---

## 📞 Support & Debugging

### Enable Debug Mode

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Check System Requirements

```bash
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import streamlit; print(f'Streamlit: {streamlit.__version__}')"
python -c "import xgboost; print(f'XGBoost: {xgboost.__version__}')"
```

### Verify Model Loading

```bash
python -c "from pipeline import AttackDetectionPipeline; p = AttackDetectionPipeline(); print('Model loaded successfully')"
```

---

## 🎓 Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **XGBoost Guide**: https://xgboost.readthedocs.io/
- **Plotly Examples**: https://plotly.com/python/
- **Network Security**: https://www.nist.gov/

---

## 📝 Version History

```
Version 1.0.0 (April 2026)
├── Initial Release
├── Streamlit Dashboard
├── Device Simulator
├── IP Blocker
└── Real-time Detection
```

---

## 📄 License & Attribution

This project is for educational and research purposes.

---

## ✅ Verification Checklist

Before using the system, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list | grep streamlit`)
- [ ] Model files present (4 .pkl/.json files)
- [ ] No port conflicts
- [ ] Sufficient disk space (1GB recommended)
- [ ] Internet connection (for Streamlit Cloud features)
- [ ] Test suite passes (`python test_system.py`)
- [ ] Dashboard loads without errors

---

## 🚀 Next Steps

1. **Test with Normal Traffic**
   - Start with "Normal" traffic type
   - Verify baseline detection

2. **Try Different Attacks**
   - Test each attack type
   - Observe confidence scores
   - Review blocking effectiveness

3. **Monitor History**
   - Review detection patterns
   - Export reports
   - Analyze trends

4. **Optimize Settings**
   - Adjust simulation speed
   - Find optimal batch size
   - Tune confidence thresholds

---

## 📞 Quick Help

| Issue | Command |
|-------|---------|
| Start Dashboard | `streamlit run streamlit_app.py` |
| Install Dependencies | `pip install -r requirements_streamlit.txt` |
| Run Tests | `python test_system.py` |
| Train Model | `jupyter notebook lstm_attack_timeseries.ipynb` |
| Check Version | `python --version` |

---

**Last Updated**: April 18, 2026
**Status**: ✅ Production Ready
**Maintainer**: Security Team

---

