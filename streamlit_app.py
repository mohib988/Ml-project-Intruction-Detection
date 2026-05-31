"""
Streamlit Dashboard for Attack Detection System
Real-time Network Topology Monitoring with Live Attack Detection
"""


import streamlit as st
import random
from datetime import datetime
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix, classification_report
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
    initial_sidebar_state="collapsed"
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
    st.session_state.simulator = DeviceSimulator()

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

# ==================== CONFIGURATION (INLINE) ====================
col_cfg_left, col_cfg_right = st.columns([3, 1])

with col_cfg_left:
    st.subheader("📊 Model Information")
    if st.session_state.pipeline.model_info:
        info = st.session_state.pipeline.model_info
        st.info(f"""
        **Model**: {info.get('model_type', 'N/A')}
        
        **Classes**: {info.get('num_classes', 'N/A')}
        
        **Accuracy**: {info.get('test_accuracy', 0)*100:.2f}%
        """)

with col_cfg_right:
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
        st.plotly_chart(fig_network, use_container_width=True, height=480)
    except Exception as e:
        st.error(f"Error rendering network: {e}")

with col_network_controls:
    st.markdown("### 📋 Legend")
    st.markdown("""
    **Device Types:**
    - 🔴 Attacker
    - � Security Camera
    - 🌡️ Smart Thermostat
    - 🔐 Door Lock
    - 📡 Motion Sensor
    - 💡 Smart Lightbulb
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

# ==================== SIMULATION SETTINGS ====================
st.markdown("### ⚙️ Simulation Settings")

col_sim1, col_sim2, col_sim3 = st.columns(3)

with col_sim1:
    attack_type = st.selectbox(
        "Select Attack Type:",
        options=[
            'Backdoor',
            'DDoS_ICMP',
            'DDoS_HTTP', 
            'DDoS_TCP_SYN',
            'DDoS_UDP',
            'Port_Scanning',
            'SQL_injection',
            'XSS',
            'OS_Fingerprinting',
            'Vulnerability_scanner',
            "Password",
            "Uploading",
            "Ransomware",
            'Normal'
        ],
        index=0,
        key="attack_type_select"
    )

with col_sim2:
    n_packets = st.slider("Packets per traffic:", 1, 10, 1, key="packets_slider")

with col_sim3:
    simulation_speed = st.slider("Simulation Speed (packets/sec):", 1, 20, 5, key="speed_slider")

st.divider()

# ==================== TARGET SELECTION ====================
st.markdown("### 🎯 Select Attack Targets")

col_atk1, col_atk2 = st.columns(2)

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

st.divider()

# Small live graph beside the simulation controls so you don't need to scroll up
if 'pulse_phase' not in st.session_state:
    st.session_state['pulse_phase'] = 0

graph_sim_placeholder = st.empty()
try:
    fig_small = create_network_graph(st.session_state.network_topology, pulse_phase=st.session_state.get('pulse_phase', 0))
    graph_sim_placeholder.plotly_chart(fig_small, use_container_width=True, height=300)
except Exception:
    pass

# ==================== ATTACK EXECUTION BUTTONS ====================
col_btn1, col_btn2, col_btn3 = st.columns([1, 3, 1])

with col_btn1:
    if st.button("🔴 LAUNCH ATTACK", use_container_width=True, key="launch_attack"):
        # Start attack on network
        attack_record = st.session_state.network_topology.start_attack(
            selected_attacker.device_id,
            selected_target.device_id,
            attack_type
        )
        print(f"Started attack: {attack_record}")
        st.session_state.current_attack = attack_record
        st.info(f"🚀 Attack initiated: {selected_attacker.device_name} → {selected_target.device_name}")
        # st.rerun()

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
               


                is_attack, result = st.session_state.pipeline.is_attack(
                    features
                )
             
                
                st.session_state.total_packets += 1
                
                if is_attack:
                    st.session_state.total_attacks += 1
                    st.session_state.network_topology.end_attack(attack, blocked=True)
                    st.session_state.detection_history.append({
                        'timestamp': datetime.now(),
                        'attacker': selected_attacker.ip_address,
                        'target': selected_target.ip_address,
                        'actual': attack['attack_type'],
                        'predicted': result['prediction'],
                        'confidence': result['confidence'],
                        'probabilities': result.get('probabilities', {}),
                        'features': features.tolist(),
                        'status': 'BLOCKED',
                        'src_ip': src_ip
                    })
                    
                    # Display detection result
                    st.success("🚨 ATTACK DETECTED AND BLOCKED!")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.metric("Actual", attack['attack_type'])
                    with col_d2:
                        st.metric("Predicted", result['prediction'])
                else:
                    st.warning("⚠️ Normal traffic - no threat detected")
                    st.session_state.detection_history.append({
                        'timestamp': datetime.now(),
                        'attacker': selected_attacker.ip_address,
                        'target': selected_target.ip_address,
                        'actual': attack['attack_type'],
                        'predicted': result.get('prediction', 'Normal'),
                        'confidence': result.get('confidence', 0.0),
                        'probabilities': result.get('probabilities', {}),
                        'features': features.tolist(),
                        'status': 'PASSED',
                        'src_ip': src_ip
                    })
                
                st.session_state.current_attack = None
                # advance pulse phase and refresh small graph
                st.session_state['pulse_phase'] = (st.session_state.get('pulse_phase', 0) + 1) % 4
                try:
                    fig_small = create_network_graph(st.session_state.network_topology, pulse_phase=st.session_state['pulse_phase'])
                    graph_sim_placeholder.plotly_chart(fig_small, use_container_width=True, height=300)
                except Exception:
                    pass

with col_btn3:
    if st.button("🚫 BLOCK ATTACKER IP", use_container_width=True, key="block_attacker"):
        st.session_state.simulator.block_ip(selected_attacker.ip_address)
        st.session_state.network_topology.block_device(selected_attacker.device_id)
        st.session_state.blocked_count += 1
        st.success(f"✓ {selected_attacker.ip_address} has been blocked")
        st.rerun()

# with col_btn4:
#     if st.button("🔓 CLEAR ALL BLOCKS", use_container_width=True, key="clear_blocks"):
#         st.session_state.simulator.clear_blocked_ips()
#         for device in st.session_state.network_topology.get_all_devices():
#             st.session_state.network_topology.unblock_device(device.device_id)
#         st.success("✓ All blocks cleared")
#         st.rerun()

# ==================== MULTI-ATTACK SIMULATION ====================
st.markdown("### 🔁 Batch Simulation")
col_sim_a, col_sim_b, col_sim_c = st.columns(3)
with col_sim_a:
    iterations = st.number_input("Number of attempts:", min_value=1, max_value=200, value=10, step=1, key='sim_iterations')
with col_sim_b:
    randomize_targets = st.checkbox("Randomize attacker/target", value=False, key='sim_randomize')
with col_sim_c:
    show_details_after = st.checkbox("Show detection details after run", value=True, key='sim_show_details')

if st.button("🎯 SIMULATE MULTIPLE ATTACKS", key='simulate_multiple'):
    progress = st.progress(0)
    status_area = st.empty()
    for i in range(int(iterations)):
        # choose attacker/target
        if randomize_targets:
            attacker = random.choice(st.session_state.network_topology.get_attackers())
            target = random.choice(st.session_state.network_topology.get_iot_devices())
        else:
            attacker = selected_attacker
            target = selected_target

        # start attack record
        attack_record = st.session_state.network_topology.start_attack(
            attacker.device_id, target.device_id, attack_type
        )
        st.session_state.current_attack = attack_record

        # generate traffic and run detection
        features, src_ip = st.session_state.simulator.generate_traffic(attack_type, n_samples=1)
        if features is None:
            status_area.warning(f"Simulation: {src_ip}")
            continue

        is_attack, result = st.session_state.pipeline.is_attack(features)

        st.session_state.total_packets += 1

        if is_attack:
            st.session_state.total_attacks += 1
            st.session_state.network_topology.end_attack(attack_record, blocked=True)
            st.session_state.detection_history.append({
                'timestamp': datetime.now(),
                'attacker': attacker.ip_address,
                'target': target.ip_address,
                'actual': attack_record.get('attack_type', attack_type),
                'predicted': result['prediction'],
                'confidence': result['confidence'],
                'probabilities': result.get('probabilities', {}),
                'features': features.tolist(),
                'status': 'BLOCKED',
                'src_ip': src_ip
            })
            status_area.success(f"[{i+1}/{iterations}] Detected and blocked: {attacker.device_name} → {target.device_name}")
        else:
            st.session_state.detection_history.append({
                'timestamp': datetime.now(),
                'attacker': attacker.ip_address,
                'target': target.ip_address,
                'actual': attack_record.get('attack_type', attack_type),
                'predicted': result.get('prediction', 'Normal'),
                'confidence': result.get('confidence', 0.0),
                'probabilities': result.get('probabilities', {}),
                'features': features.tolist(),
                'status': 'PASSED',
                'src_ip': src_ip
            })
            status_area.info(f"[{i+1}/{iterations}] No threat detected from {attacker.device_name}")

        # optional pacing
        time.sleep(max(0.0, 1.0 / max(1, simulation_speed)))
        progress.progress((i + 1) / int(iterations))
        # update pulse and small graph
        st.session_state['pulse_phase'] = (st.session_state.get('pulse_phase', 0) + 1) % 4
        try:
            fig_small = create_network_graph(st.session_state.network_topology, pulse_phase=st.session_state['pulse_phase'])
            graph_sim_placeholder.plotly_chart(fig_small, use_container_width=True, height=300)
        except Exception:
            pass

    # Show visual summaries
    st.divider()
    st.subheader("📈 Attack Detection Summary")
    
    # Detection accuracy metrics
    if st.session_state.detection_history:
        hist_data = st.session_state.detection_history
        
        # Extract actual and predicted labels
        y_actual = [h.get('actual', h.get('attack_type', 'Unknown')) for h in hist_data]
        y_predicted = [h.get('predicted', h.get('attack_type', 'Unknown')) for h in hist_data]
        
        # Metrics row
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            correct = sum(1 for a, p in zip(y_actual, y_predicted) if a == p)
            st.metric("✅ Correct Predictions", f"{correct}/{len(y_actual)}")
        with col_m2:
            accuracy = correct / len(y_actual) * 100 if y_actual else 0
            st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
        with col_m3:
            blocked = sum(1 for h in hist_data if h['status'] == 'BLOCKED')
            st.metric("🚫 Attacks Blocked", blocked)
        with col_m4:
            passed = sum(1 for h in hist_data if h['status'] == 'PASSED')
            st.metric("⚠️ Passed Undetected", passed)
        
        st.divider()
        
        # Actual vs Predicted Counts
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("**Actual Attack Distribution**")
            actual_counts = pd.Series(y_actual).value_counts().sort_values(ascending=False)
            fig_actual = go.Figure(data=[
                go.Bar(x=actual_counts.index, y=actual_counts.values, marker_color='lightblue')
            ])
            fig_actual.update_layout(title="Actual Attacks", xaxis_title="Attack Type", yaxis_title="Count", showlegend=False, height=350)
            st.plotly_chart(fig_actual, use_container_width=True)
        
        with col_c2:
            st.markdown("**Predicted Attack Distribution**")
            pred_counts = pd.Series(y_predicted).value_counts().sort_values(ascending=False)
            fig_pred = go.Figure(data=[
                go.Bar(x=pred_counts.index, y=pred_counts.values, marker_color='lightcoral')
            ])
            fig_pred.update_layout(title="Predicted Attacks", xaxis_title="Attack Type", yaxis_title="Count", showlegend=False, height=350)
            st.plotly_chart(fig_pred, use_container_width=True)
        
        st.divider()
        
        # Confusion Matrix
        st.markdown("**Confusion Matrix - Actual vs Predicted**")
        unique_labels = sorted(set(y_actual + y_predicted))
        cm = confusion_matrix(y_actual, y_predicted, labels=unique_labels)
        
        # Create heatmap
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm,
            x=unique_labels,
            y=unique_labels,
            colorscale='Blues',
            text=cm,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        fig_cm.update_layout(
            title="Confusion Matrix: True Labels vs Predicted",
            xaxis_title="Predicted Label",
            yaxis_title="True Label",
            height=500,
            width=600
        )
        st.plotly_chart(fig_cm, use_container_width=True)
        
        st.divider()
    
    # Attack flow
    flow_df = create_attack_flow_visualization(st.session_state.network_topology)
    if flow_df is not None and not flow_df.empty:
        st.markdown("**Attack Flow (recent active attacks)**")
        st.dataframe(flow_df, use_container_width=True)

    # Attack timeline
    timeline_fig = create_attack_timeline(st.session_state.network_topology)
    if timeline_fig is not None:
        st.markdown("**Attack Timeline by Type**")
        st.plotly_chart(timeline_fig, use_container_width=True)

    # Attack matrix
    matrix_df = create_attack_matrix(st.session_state.network_topology)
    if matrix_df is not None and not matrix_df.empty:
        st.markdown("**Attack Source → Target Matrix**")
        st.dataframe(matrix_df, use_container_width=True)

    # Detection history
    if st.session_state.detection_history:
        st.markdown("**Detection History**")
        hist_df = pd.DataFrame([{
            'time': h['timestamp'].strftime('%H:%M:%S'),
            'attacker': h['attacker'],
            'target': h['target'],
            'actual': h.get('actual', 'N/A'),
            'predicted': h.get('predicted', h.get('attack_type', 'N/A')),
            'confidence': f"{h['confidence']*100:.1f}%",
            'status': h['status']
        } for h in st.session_state.detection_history])
        st.dataframe(hist_df, use_container_width=True)

        if show_details_after:
            idx = st.selectbox("Select detection to inspect:", list(range(len(st.session_state.detection_history))), format_func=lambda i: f"{i} - {st.session_state.detection_history[i]['attacker']} → {st.session_state.detection_history[i]['target']}")
            rec = st.session_state.detection_history[int(idx)]
            
            col_det1, col_det2, col_det3 = st.columns(3)
            with col_det1:
                st.metric("Actual Label", rec.get('actual', 'N/A'))
            with col_det2:
                st.metric("Predicted Label", rec.get('predicted', 'N/A'))
            with col_det3:
                is_correct = rec.get('actual') == rec.get('predicted')
                st.metric("Correct", "✅ Yes" if is_correct else "❌ No")
            
            st.markdown(f"**Confidence:** {rec['confidence']*100:.1f}%")
            probs = rec.get('probabilities', {})
            if probs:
                probs_df = pd.DataFrame(list(probs.items()), columns=['Class', 'Probability']).sort_values('Probability', ascending=False)
                st.dataframe(probs_df, use_container_width=True)

            # show top feature values (by absolute value)
            feats = rec.get('features')
            if feats:
                feat_series = pd.Series(feats)
                top_idx = feat_series.abs().sort_values(ascending=False).head(10).index
                top_vals = feat_series.iloc[top_idx]
                feature_names = [f"feature_{i}" for i in top_vals.index]
                feat_df = pd.DataFrame({'feature_name': feature_names, 'value': top_vals.values})
                st.markdown("**Top feature values (by magnitude)**")
                st.dataframe(feat_df, use_container_width=True)

    st.success("Simulation complete")
    # st.rerun()

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