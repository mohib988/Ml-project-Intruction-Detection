"""
Streamlit Dashboard for Attack Detection System
Real-time Network Topology Monitoring with Live Attack Detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from pipeline import AttackDetectionPipeline
from device_simulator import DeviceSimulator
from network_topology import NetworkTopology
from network_visualization import (
    create_network_graph, create_device_status_table, 
    create_attack_flow_visualization, create_attack_timeline,
     create_attack_matrix
)


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title=" Attack Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM STYLING ====================
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .attack-detected {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        margin: 10px 0;
    }
    .safe-status {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        margin: 10px 0;
    }
    .blocked-ip {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = AttackDetectionPipeline()

if 'simulator' not in st.session_state:
    n_features = st.session_state.pipeline.model_info['n_features'] if st.session_state.pipeline.model_info else 100
    st.session_state.simulator = DeviceSimulator(n_features=n_features)

if 'network_topology' not in st.session_state:
    st.session_state.network_topology = NetworkTopology(n_iot_devices=5, n_attackers=2)

if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

if 'total_packets' not in st.session_state:
    st.session_state.total_packets = 0

if 'total_attacks' not in st.session_state:
    st.session_state.total_attacks = 0

if 'blocked_count' not in st.session_state:
    st.session_state.blocked_count = 0

if 'current_attack' not in st.session_state:
    st.session_state.current_attack = None

# ==================== MAIN TITLE ====================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; color: #667eea;'> Network Attack Detection System</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Real-time threat detection with AI-powered analytics</p>", 
                unsafe_allow_html=True)

st.divider()

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    st.markdown("# ⚙️ Configuration")
    
    st.subheader("📊 Model Information")
    if st.session_state.pipeline.model_info:
        info = st.session_state.pipeline.model_info
        st.info(f"""
        **Model**: {info.get('model_type', 'N/A')}
        
        **Classes**: {info.get('num_classes', 'N/A')}
        
        **Accuracy**: {info.get('test_accuracy', 0)*100:.2f}%
        """)
    
    st.divider()
    
    st.subheader("🎮 Simulation Settings")
    
    attack_type = st.selectbox(
        "Select Attack Type:",
        options=[
            'DDoS_HTTP_Flood_attack',
            'DDoS_TCP_SYN_Flood_attack', 
            'DDoS_UDP_Flood_attack',
            'Port_Scanning_attack',
            'SQL_injection_attack',
            'XSS_attack',
            'Backdoor_attack',
            'MITM_attack',
            'Normal'
        ],
        index=0
    )
    
    n_packets = st.slider("Packets per traffic:", 1, 10, 1)
    simulation_speed = st.slider("Simulation Speed (packets/sec):", 1, 20, 5)
    
    st.divider()
    
    st.subheader("🔧 System Control")
    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.detection_history = []
        st.session_state.total_packets = 0
        st.session_state.total_attacks = 0
        st.session_state.blocked_count = 0
        st.session_state.current_attack = None
        st.session_state.network_topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        st.session_state.simulator.clear_blocked_ips()
        st.session_state.simulator.clear_history()
        st.rerun()
    
    st.divider()
    
    col_block1, col_block2 = st.columns(2)
    with col_block1:
        st.metric("📦 Packets", st.session_state.total_packets)
    with col_block2:
        st.metric("⚠️ Attacks", st.session_state.total_attacks)


# ==================== MAIN NETWORK TOPOLOGY DISPLAY ====================
col_network_main, col_network_controls = st.columns([3, 1])

with col_network_main:
    st.subheader("🌐 Network Topology - Live Monitoring")
    
    # Display network graph
    try:
        fig_network = create_network_graph(st.session_state.network_topology)
        st.plotly_chart(fig_network, use_container_width=True, height=600)
    except Exception as e:
        st.error(f"Error rendering network: {e}")

with col_network_controls:
    st.markdown("### 📋 Legend")
    st.markdown("""
    **Device Types:**
    - 🔴 Attacker
    - 🟢 IoT Device
    - 🟡 Gateway
    - 🟣 Server
    
    **Status:**
    - Teal: Safe ✅
    - Gold: Under Attack ⚠️
    - Orange: Attacked 🔴
    
    **Connections:**
    - Gray: Normal
    - Red: Attack
    """)

st.divider()

# ==================== REAL-TIME NETWORK METRICS ====================
st.subheader("📊 Real-Time Network Metrics")

col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.metric("🌐 Total Devices", st.session_state.network_topology.get_network_stats()['total_devices'])

with col_metric2:
    st.metric("⚠️ Under Attack", st.session_state.network_topology.get_network_stats()['under_attack'])

with col_metric3:
    st.metric("🔴 Attacked", st.session_state.network_topology.get_network_stats()['attacked'])

with col_metric4:
    total = st.session_state.network_topology.get_network_stats()['total_devices']
    attacked = st.session_state.network_topology.get_network_stats()['attacked']
    st.metric("🛡️ Safe", total - attacked)

st.divider()

# ==================== ATTACK SIMULATION INTERFACE ====================
st.subheader("🎮 Attack Simulation & Detection")

col_atk1, col_atk2, col_atk3 = st.columns(3)

with col_atk1:
    st.markdown("**Select Attacker Device:**")
    attackers = st.session_state.network_topology.get_attackers()
    attacker_names = [f"{a.device_name} ({a.ip_address})" for a in attackers]
    selected_attacker_idx = st.selectbox("Attacker", range(len(attackers)), format_func=lambda i: attacker_names[i], key="attacker_select")
    selected_attacker = attackers[selected_attacker_idx]

with col_atk2:
    st.markdown("**Select Target IoT Device:**")
    iot_devices = st.session_state.network_topology.get_iot_devices()
    iot_names = [f"{d.device_name} ({d.ip_address})" for d in iot_devices]
    selected_target_idx = st.selectbox("Target", range(len(iot_devices)), format_func=lambda i: iot_names[i], key="target_select")
    selected_target = iot_devices[selected_target_idx]

with col_atk3:
    st.markdown("**Selected Attack Type:**")
    st.markdown(f"<div class='device-card'><strong>{attack_type}</strong></div>", unsafe_allow_html=True)

st.divider()

# ==================== ATTACK EXECUTION BUTTONS ====================
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("🔴 LAUNCH ATTACK", use_container_width=True, key="launch_attack"):
        # Start attack on network
        attack_record = st.session_state.network_topology.start_attack(
            selected_attacker.device_id,
            selected_target.device_id,
            attack_type
        )
        st.session_state.current_attack = attack_record
        st.info(f"🚀 Attack initiated: {selected_attacker.device_name} → {selected_target.device_name}")

with col_btn2:
    if st.button("🛡️ RUN DETECTION", use_container_width=True, key="detect_attack"):
        if st.session_state.current_attack:
            attack = st.session_state.current_attack
            
            # Generate realistic attack traffic
            features, src_ip = st.session_state.simulator.generate_traffic(
                attack['attack_type'], n_samples=1
            )
            
            if features is not None:
                # Run ML detection
                is_attack, result = st.session_state.pipeline.is_attack(features[0])
                
                st.session_state.total_packets += 1
                
                if is_attack:
                    st.session_state.total_attacks += 1
                    st.session_state.network_topology.end_attack(attack, blocked=True)
                    st.session_state.detection_history.append({
                        'timestamp': datetime.now(),
                        'attacker': selected_attacker.ip_address,
                        'target': selected_target.ip_address,
                        'attack_type': result['prediction'],
                        'confidence': result['confidence'],
                        'status': 'BLOCKED',
                        'src_ip': src_ip
                    })
                    
                    # Display detection result
                    st.success("🚨 ATTACK DETECTED AND BLOCKED!")
                    
                    col_d1, col_d2, col_d3 = st.columns(3)
                    with col_d1:
                        st.metric("Detected Attack", result['prediction'])
                    with col_d2:
                        st.metric("Confidence", f"{result['confidence']*100:.1f}%")
                    with col_d3:
                        st.metric("Status", "BLOCKED ✓")
                else:
                    st.warning("⚠️ Normal traffic - no threat detected")
                
                st.session_state.current_attack = None

with col_btn3:
    if st.button("🚫 BLOCK ATTACKER IP", use_container_width=True, key="block_attacker"):
        st.session_state.simulator.block_ip(selected_attacker.ip_address)
        st.session_state.network_topology.block_device(selected_attacker.device_id)
        st.session_state.blocked_count += 1
        st.success(f"✓ {selected_attacker.ip_address} has been blocked")
        st.rerun()

with col_btn4:
    if st.button("🔓 CLEAR ALL BLOCKS", use_container_width=True, key="clear_blocks"):
        st.session_state.simulator.clear_blocked_ips()
        for device in st.session_state.network_topology.get_all_devices():
            st.session_state.network_topology.unblock_device(device.device_id)
        st.success("✓ All blocks cleared")
        st.rerun()

st.divider()

# ==================== DEVICE STATUS TABLE ====================
st.subheader("📋 Device Status Table")

device_df = create_device_status_table(st.session_state.network_topology)
st.dataframe(device_df, use_container_width=True, hide_index=True)

st.divider()

# ==================== SUMMARY METRICS ====================
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.metric("📊 Total Packets Analyzed", st.session_state.total_packets)

with col_footer2:
    st.metric("⚠️ Total Attacks Detected", st.session_state.total_attacks)

with col_footer3:
    detection_rate = (st.session_state.total_attacks / max(st.session_state.total_packets, 1) * 100)
    st.metric("📈 Detection Rate", f"{detection_rate:.1f}%")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 12px;'>🛡️ Advanced ML-based Network Attack Detection System | Real-time Topology Monitoring</p>", 
            unsafe_allow_html=True)
