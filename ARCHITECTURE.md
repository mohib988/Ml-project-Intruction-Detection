# 🛡️ SHIELD - Attack Detection System
## Project Summary & Architecture

---

## 📌 Project Overview

**SHIELD** (Smart Hosted Intrusion Event & Load Detection) is a comprehensive network threat detection and response system combining:
- Machine Learning threat classification
- Real-time network simulation
- Interactive web dashboard
- Automated threat response

---

## 📁 Project Structure

```
d:\advanceMlProject\
│
├── 📊 TRAINING & DATA
│   ├── lstm_attack_timeseries.ipynb      # Model training notebook
│   ├── Dataset/                          # Training datasets
│   │   ├── Backdoor_attack.csv
│   │   ├── DDoS_*_attack.csv (3 types)
│   │   ├── MITM_attack.csv
│   │   ├── OS_Fingerprinting_attack.csv
│   │   ├── Password_attack.csv
│   │   ├── Port_Scanning_attack.csv
│   │   ├── Ransomware_attack.csv
│   │   ├── SQL_injection_attack.csv
│   │   ├── Uploading_attack.csv
│   │   ├── Vulnerability_scanner_attack.csv
│   │   ├── XSS_attack.csv
│   │   └── NormalClass/                  # Normal traffic
│   │       ├── Distance.csv
│   │       ├── Flame_Sensor.csv
│   │       ├── Heart_Rate.csv
│   │       ├── IR_Receiver.csv
│   │       └── Modbus.csv
│   └── DNN-EdgeIIoT-dataset.csv
│
├── 🤖 MODEL & ARTIFACTS
│   ├── xgboost_attack_detection_model.pkl
│   ├── xgboost_attack_detection_model.json
│   ├── scaler.pkl                        # Feature normalization
│   ├── label_encoder.pkl                 # Class encoding
│   └── model_info.json                   # Metadata
│
├── 💻 CORE MODULES
│   ├── pipeline.py                       # Prediction pipeline
│   ├── device_simulator.py               # Traffic simulation
│   └── streamlit_app.py                  # Web dashboard
│
├── 🚀 EXECUTION SCRIPTS
│   ├── start_dashboard.py                # Python launcher
│   ├── setup_and_run.bat                 # Windows setup
│   ├── setup_and_run.sh                  # Linux/Mac setup
│   └── test_system.py                    # System testing
│
├── 📚 DOCUMENTATION
│   ├── README_STREAMLIT.md               # Feature guide
│   ├── COMPLETE_SETUP_GUIDE.md           # Setup instructions
│   ├── ARCHITECTURE.md                   # This file
│   └── requirements_streamlit.txt        # Dependencies
│
└── 🏗️ UTILITIES
    └── main.py                           # (Legacy)
```

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                      Streamlit Dashboard                        │
│  ┌─────────────┬──────────────┬────────────┬───────────────┐   │
│  │ Real-time   │ Statistics   │ IP Blocker │ History &     │   │
│  │ Monitor     │ & Analytics  │ Management │ Audit Trail   │   │
│  └─────────────┴──────────────┴────────────┴───────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                  APPLICATION LOGIC LAYER                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────┐        ┌──────────────────────────┐  │
│  │ Attack Detection    │        │ Device Simulator         │  │
│  │ Pipeline            │        │ (Traffic Generation)     │  │
│  │                     │        │                          │  │
│  │ • Load Model        │        │ • 9 Attack Types         │  │
│  │ • Scale Features    │        │ • Traffic Patterns       │  │
│  │ • Make Prediction   │        │ • IP Tracking            │  │
│  │ • Get Scores        │        │ • IP Blocking            │  │
│  │ • Return Labels     │        │ • History Logging        │  │
│  └──────────┬──────────┘        └────────────┬─────────────┘  │
│             │                                 │                │
│  ┌──────────▼──────────┐        ┌────────────▼─────────────┐  │
│  │ Session Management  │        │ Data Storage            │  │
│  │ (Streamlit State)   │        │ & History               │  │
│  │                     │        │                         │  │
│  │ • Detection History │        │ • Detection Events      │  │
│  │ • Blocked IPs       │        │ • Metrics               │  │
│  │ • Metrics/Stats     │        │ • Audit Trail           │  │
│  └─────────────────────┘        └─────────────────────────┘  │
│                                                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                    ML MODEL LAYER                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         XGBoost Classifier (Trained)                    │ │
│  │                                                          │ │
│  │  • Algorithm: Gradient Boosting                         │ │
│  │  • Trees: 200                                           │ │
│  │  • Max Depth: 8                                         │ │
│  │  • Input Features: 100 (normalized)                    │ │
│  │  • Output Classes: 9 attack types + Normal             │ │
│  │  • Accuracy: ~92% (test set)                           │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Feature Preprocessing                                 │ │
│  │                                                          │ │
│  │  • StandardScaler (Zero mean, Std=1)                   │ │
│  │  • One-hot Encoding (Categorical → Numeric)            │ │
│  │  • Feature Selection (100 most important)              │ │
│  │  • Scale Range: [-5, +5]                               │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                  DATA LAYER                                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Model Artifacts:                                              │
│  ├── xgboost_attack_detection_model.pkl                       │
│  ├── scaler.pkl (StandardScaler)                              │
│  ├── label_encoder.pkl (Attack Classes)                       │
│  └── model_info.json (Metadata)                               │
│                                                                │
│  Training Data:                                                │
│  ├── 14 Different Attack Types (CSVs)                         │
│  ├── Normal Traffic Baseline                                  │
│  └── 100+ Features per record                                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

### Attack Detection Flow

```
                    START
                     │
                     ▼
        ┌────────────────────────┐
        │  1. Network Traffic    │  Source: Device Simulator
        │     Captured/Generated │  - Normal or Attack traffic
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  2. Feature Extraction │  100+ network features
        │     & Preprocessing    │  - Packet statistics
        └────────────┬───────────┘  - Protocol patterns
                     │              - Rate metrics
                     ▼
        ┌────────────────────────┐
        │  3. Feature Scaling    │  StandardScaler
        │  (Normalization)       │  - Mean=0, Std=1
        └────────────┬───────────┘  - Range [-5, +5]
                     │
                     ▼
        ┌────────────────────────┐
        │  4. ML Model Inference │  XGBoost
        │  (XGBoost Classifier)  │  200 trees
        └────────────┬───────────┘  9 classes
                     │
                     ▼
        ┌────────────────────────────────────────┐
        │  5. Classification Output              │
        │  ├── Predicted Class (Attack Type)     │
        │  ├── Confidence Scores (Probabilities) │
        │  └── Classification Score (Max Proba)  │
        └────────────┬────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐         ┌─────────────┐
    │ Is Attack?  │         │ Normal?     │
    │ Score > 50% │         │ Score > 50% │
    └──────┬──────┘         └──────┬──────┘
           │                       │
    YES───▼                        │───NO
    │                             │
    ▼                             ▼
┌──────────────────┐    ┌──────────────────┐
│  6a. ATTACK      │    │  6b. NORMAL      │
│  DETECTED        │    │  TRAFFIC         │
│                  │    │                  │
│ • Log event      │    │ • Log event      │
│ • Confidence: XX% │    │ • Confidence: XX% │
│ • Source IP: xxx │    │ • Source IP: xxx │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │ 7a. BLOCK IP     │    │ 7b. ALLOW        │
    │                  │    │                  │
    │ • Add to list    │    │ • No action      │
    │ • Log block      │    │ • Continue       │
    │ • Update stats   │    │ • Monitor        │
    └────────┬─────────┘    └────────┬─────────┘
             │                       │
             └───────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  8. Update Dashboard   │
            │                        │
            │ • Refresh metrics      │
            │ • Update charts        │
            │ • Log to history       │
            │ • Display notification │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  9. Update Session     │
            │     State              │
            │                        │
            │ • Packet count         │
            │ • Attack count         │
            │ • Blocked IPs          │
            │ • Detection history    │
            └────────────┬───────────┘
                         │
                         ▼
                    CONTINUE MONITORING
```

---

## 🎮 Device Simulator Architecture

### Traffic Generation System

```
DeviceSimulator Class
│
├── __init__()
│   ├── n_features: 100
│   ├── noise_level: 0.1
│   ├── blocked_ips: Set[]
│   └── traffic_history: List[]
│
├── Attack Pattern Generators
│   ├── _create_normal_pattern()
│   │   └── Base traffic: N(0.5, 0.2)
│   │
│   ├── _create_ddos_pattern()
│   │   └── High request rate: N(0.8, 0.1)
│   │
│   ├── _create_syn_pattern()
│   │   └── High SYN flags: N(0.7, 0.15)
│   │
│   ├── _create_udp_pattern()
│   │   └── High UDP traffic: N(0.75, 0.12)
│   │
│   ├── _create_port_scan_pattern()
│   │   └── Many ports: N(0.4, 0.2)
│   │
│   ├── _create_sql_injection_pattern()
│   │   └── SQL patterns: N(0.5, 0.15)
│   │
│   ├── _create_xss_pattern()
│   │   └── Script injection: N(0.5, 0.15)
│   │
│   ├── _create_backdoor_pattern()
│   │   └── Command patterns: N(0.6, 0.15)
│   │
│   └── _create_mitm_pattern()
│       └── Protocol anomalies: N(0.55, 0.15)
│
├── generate_traffic(attack_type, n_samples, src_ip)
│   └── Returns: (features [1,100], src_ip)
│
├── IP Management
│   ├── block_ip(ip_address)
│   ├── unblock_ip(ip_address)
│   ├── get_blocked_ips()
│   └── clear_blocked_ips()
│
└── History
    ├── add_to_history(record)
    ├── get_history()
    └── clear_history()
```

---

## 💾 Data Storage Architecture

### Session State Management

```
Streamlit Session State (st.session_state)
│
├── pipeline
│   ├── model: XGBClassifier
│   ├── scaler: StandardScaler
│   ├── encoder: LabelEncoder
│   └── model_info: Dict
│
├── simulator
│   ├── n_features: 100
│   ├── noise_level: 0.1
│   ├── blocked_ips: Set
│   └── traffic_history: List
│
├── Metrics
│   ├── total_packets: int
│   ├── total_attacks: int
│   └── blocked_count: int
│
├── Detection History
│   └── detection_history: List[Dict]
│       ├── timestamp: datetime
│       ├── src_ip: str
│       ├── attack_type: str
│       ├── confidence: float
│       └── action: str
│
└── UI/UX State
    ├── current_tab: str
    ├── simulation_active: bool
    └── filter_settings: Dict
```

---

## 🔐 Security Architecture

### IP Blocking System

```
┌─────────────────────────────────────┐
│  Incoming Traffic                   │
└────────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ IP Lookup in        │
    │ Blocked IP Set      │
    └─────────┬───────────┘
              │
      ┌───────┴───────┐
      │               │
    YES              NO
      │               │
      ▼               ▼
  ┌────────┐    ┌──────────────┐
  │BLOCKED │    │Send to ML    │
  │REJECT  │    │Detector      │
  └────────┘    └──────┬───────┘
                       │
                       ▼
            ┌──────────────────────┐
            │Threat Classification │
            │(XGBoost Model)       │
            └──────────┬───────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
         ATTACK                 NORMAL
           │                       │
           ▼                       ▼
        ┌────────┐         ┌──────────┐
        │BLOCK   │         │ALLOW     │
        │ IP     │         │FORWARD   │
        └────────┘         └──────────┘
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
        ┌────────────────────────────┐
        │Log to Detection History    │
        │Update Metrics              │
        │Update Dashboard            │
        └────────────────────────────┘
```

---

## 📊 Dashboard Component Hierarchy

```
┌─ Streamlit App (streamlit_app.py)
│
├─ Page Configuration
│   ├── Title: 🛡️ Network Attack Detection System
│   ├── Layout: Wide
│   └── Theme: Default + Custom CSS
│
├─ Session State Initialization
│   ├── pipeline
│   ├── simulator
│   ├── detection_history
│   ├── total_packets
│   ├── total_attacks
│   └── blocked_count
│
├─ Sidebar Configuration
│   ├── Model Information Display
│   ├── Simulation Settings
│   │   ├── Attack type selector
│   │   ├── Packets per traffic slider
│   │   └── Simulation speed slider
│   ├── System Control
│   │   └── Reset button
│   └── Quick Metrics
│
├─ Main Tabs
│
│   ├─ Tab 1: Real-time Monitor
│   │   ├── Top Metrics (Safe/Attacks/Blocked)
│   │   ├── Simulation Controls
│   │   ├── Live Results Display
│   │   │   ├── Attack alerts (red)
│   │   │   ├── Normal traffic (green)
│   │   │   ├── Threat probabilities
│   │   │   └── Block button
│   │   └── Animation placeholders
│   │
│   ├─ Tab 2: Statistics & Analytics
│   │   ├── Summary Metrics
│   │   │   ├── Total packets
│   │   │   ├── Attacks found
│   │   │   ├── Normal traffic
│   │   │   └── Detection rate
│   │   ├── Attack Distribution (Pie)
│   │   ├── Confidence Scores (Histogram)
│   │   └── Timeline (Scatter)
│   │
│   ├─ Tab 3: IP Blocker
│   │   ├── Active Blocked IPs List
│   │   │   └── Each IP with unblock button
│   │   ├── Manual IP Blocking
│   │   │   ├── Text input
│   │   │   └── Block button
│   │   ├── Statistics
│   │   │   ├── Total blocked
│   │   │   ├── Attacks blocked
│   │   │   └── Block rate
│   │   └── Clear all button
│   │
│   └─ Tab 4: History & Audit Trail
│       ├── Filter Controls
│       │   ├── Action filter
│       │   └── IP filter
│       ├── Data Table
│       │   ├── Timestamp
│       │   ├── Source IP
│       │   ├── Attack Type
│       │   ├── Confidence
│       │   └── Action
│       └── Export CSV button
│
├─ Custom Styling (CSS)
│   ├── Gradients
│   ├── Card styles
│   ├── Color schemes
│   └── Animations
│
└─ Footer
    └── Attribution & Info
```

---

## 🔄 Call Flow Diagram

### From User Interaction to Threat Response

```
USER ACTION
    │
    ├─ Select Attack Type (Dropdown)
    ├─ Set Packets (Slider)
    ├─ Click "Start Simulation"
    │
    ▼
APP_LOGIC
    │
    ├─ Generate traffic → simulator.generate_traffic()
    │   │
    │   ├─ Check if IP is blocked
    │   ├─ Generate pattern based on attack type
    │   ├─ Add noise
    │   └─ Return (features, src_ip)
    │
    ├─ Make prediction → pipeline.predict_single()
    │   │
    │   ├─ Scale features using scaler
    │   ├─ Feed to XGBoost model
    │   └─ Get predictions + probabilities
    │
    ├─ Classify result → is_attack()
    │   │
    │   ├─ Check if prediction != 'Normal'
    │   ├─ Get confidence score
    │   └─ Return (is_attack, result_dict)
    │
    ├─ Update session state
    │   │
    │   ├─ Increment total_packets
    │   ├─ Increment total_attacks (if attack)
    │   ├─ Add to detection_history
    │   └─ Update metrics
    │
    ├─ Take action
    │   │
    │   ├─ IF attack
    │   │   ├─ Display alert (red)
    │   │   ├─ Show confidence
    │   │   ├─ Provide block button
    │   │   └─ Log event
    │   │
    │   └─ ELSE (normal)
    │       ├─ Display ok (green)
    │       ├─ Show confidence
    │       └─ Continue monitoring
    │
    └─ Render update → Streamlit
        │
        └─ Display results + charts
```

---

## 📈 Performance Characteristics

### Speed & Efficiency

```
Operation                  | Time       | Notes
─────────────────────────────────────────────────────
Create Simulator           | ~10ms      | One-time
Generate Traffic (1)       | ~5ms       | Per sample
Scale Features (1)         | ~2ms       | StandardScaler
XGBoost Prediction (1)     | ~30ms      | Tree traversal
Full Pipeline (1)          | ~40ms      | Total
Process Batch (10)         | ~150ms     | 10 samples
Dashboard Refresh          | ~500ms     | Render + update
```

### Memory Usage

```
Component              | Memory    | Notes
──────────────────────────────────────────
XGBoost Model         | ~50MB     | 200 trees
Scaler                | ~1MB      | StandardScaler
Label Encoder         | <1MB      | 9 classes
Simulation History    | ~10-50MB  | 1000-5000 records
Session State         | ~20MB     | All stored data
Total Runtime         | ~300MB    | Peak usage
```

---

## 🎯 Attack Classification Matrix

```
Attack Type                 | Confidence Range | Typical Pattern
────────────────────────────────────────────────────────────────────
Normal                      | 85-98%          | Low noise, balanced
DDoS_HTTP_Flood_attack     | 90-99%          | High request rate
DDoS_TCP_SYN_Flood_attack  | 88-97%          | High SYN flags
DDoS_UDP_Flood_attack      | 87-96%          | High UDP volume
Port_Scanning_attack       | 85-95%          | Sequential ports
SQL_injection_attack       | 82-93%          | SQL keywords
XSS_attack                 | 80-92%          | Script patterns
Backdoor_attack            | 85-94%          | Command patterns
MITM_attack                | 78-90%          | Protocol anomalies
```

---

## 🔌 API Endpoints (Future Enhancement)

```
POST /predict
├── Input: Network features
└── Output: {prediction, confidence, action}

GET /status
└── Output: System statistics and metrics

POST /block_ip
├── Input: IP address
└── Output: {status, message}

GET /blocked_ips
└── Output: List of blocked IP addresses

GET /history
├── Query: ?limit=100&filter=attack
└── Output: Detection history records

POST /export_history
└── Output: CSV file download
```

---

## 🛡️ Security Considerations

### Threat Model

```
Threats Addressed:
├── DDoS Attacks (HTTP, TCP, UDP)
├── Port Scanning
├── SQL Injection
├── Cross-site Scripting (XSS)
├── Backdoor Installation
├── Man-in-the-Middle (MITM)
└── Various Protocol Attacks

Not Addressed:
├── Zero-day exploits
├── Encrypted traffic analysis
├── Advanced obfuscation
└── Kernel-level attacks
```

### Mitigation Strategies

```
Prevention:
├── ML-based threat classification
├── Real-time detection
├── Automated IP blocking
└── Pattern recognition

Detection:
├── Statistical analysis
├── Confidence scoring
├── Behavioral profiling
└── Anomaly detection

Response:
├── Automatic blocking
├── Alert generation
├── History logging
└── Admin notification
```

---

## 📦 Dependencies & Requirements

### Python Packages

```
Core ML:
├── pandas==2.0.3           (Data processing)
├── numpy==1.24.3           (Numerical computing)
├── scikit-learn==1.3.0     (Preprocessing, metrics)
└── xgboost==2.0.0          (ML model)

Visualization:
├── plotly==5.17.0          (Interactive charts)
└── streamlit==1.28.0       (Web framework)
```

### System Requirements

```
Minimum:
├── Python 3.8
├── 2GB RAM
├── 500MB Disk space
└── Modern web browser

Recommended:
├── Python 3.10+
├── 4GB+ RAM
├── 2GB Disk space
└── Chrome/Firefox/Edge
```

---

## 🔄 Integration Points

### Input Integration

```
Network Sources:
├── Packet capture (pcap)
├── Flow data (NetFlow)
├── Syslog events
├── Custom APIs
└── CSV/JSON files
```

### Output Integration

```
External Systems:
├── SIEM platforms
├── Firewall APIs
├── Email notifications
├── Webhook endpoints
├── Database logging
└── File export (CSV)
```

---

## 📝 Version & Updates

### Current Version: 1.0.0

```
Releases:
├── v1.0.0 (Apr 2026)
│   ├── Initial release
│   ├── 9 attack types
│   ├── Real-time dashboard
│   └── IP blocking
│
├── v1.1.0 (Future)
│   ├── API endpoints
│   ├── External integrations
│   └── Advanced analytics
│
└── v2.0.0 (Future)
    ├── Deep learning models
    ├── Multi-model ensemble
    └── Cloud deployment
```

---

## 📞 Support & Maintenance

### Debugging

```
Check:
├── Model file presence
├── Dependencies installed
├── Port availability
├── Python version
└── System resources
```

### Updates

```
Keep Updated:
├── pip install --upgrade xgboost
├── pip install --upgrade streamlit
├── pip install --upgrade plotly
└── pip install --upgrade scikit-learn
```

---

**Last Updated**: April 18, 2026
**Status**: ✅ Production Ready
**Maintainer**: Security Team

