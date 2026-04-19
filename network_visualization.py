"""
Network Visualization Helper
Creates network graphs and visualizations for topology display
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from network_topology import NetworkTopology


def create_network_graph(topology):
    """
    Create an interactive network graph using Plotly
    
    Args:
        topology: NetworkTopology object
        
    Returns:
        Plotly figure object
    """
    graph_data = topology.get_network_graph_data()
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    # Prepare node data
    node_x = [n['x'] for n in nodes]
    node_y = [n['y'] for n in nodes]
    node_colors = [n['color'] for n in nodes]
    node_sizes = [n['size'] for n in nodes]
    node_labels = [f"{n['label']}<br>{n['ip']}" for n in nodes]
    
    # Create figure
    fig = go.Figure()
    
    # Add edges
    for edge in edges:
        src = next((n for n in nodes if n['id'] == edge['source']), None)
        tgt = next((n for n in nodes if n['id'] == edge['target']), None)
        
        if src and tgt:
            fig.add_trace(go.Scatter(
                x=[src['x'], tgt['x'], None],
                y=[src['y'], tgt['y'], None],
                mode='lines',
                line=dict(width=edge['width'], color=edge['color']),
                hoverinfo='none',
                showlegend=False
            ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            opacity=0.9
        ),
        text=[n['label'] for n in nodes],
        textposition="top center",
        textfont=dict(size=10, color='white', family='Arial Black'),
        hovertext=node_labels,
        hoverinfo='text',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title='🌐 Network Topology - Live Attack Detection',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        plot_bgcolor='#0f1a26',
        paper_bgcolor='#0f1a26',
        font=dict(color='white', size=11),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=None,
        height=600,
        dragmode='pan'
    )
    
    return fig


def create_device_status_table(topology):
    """Create device status table"""
    devices = topology.get_all_devices()
    
    data = []
    for device in devices:
        data.append({
            'Device Name': device.device_name,
            'Type': device.device_type.upper(),
            'IP Address': device.ip_address,
            'Status': device.status,
            'Attacks': device.attack_count,
            'Active': '🟢 Yes' if device.is_active else '🔴 No'
        })
    
    df = pd.DataFrame(data)
    return df


def create_attack_flow_visualization(topology):
    """Create visualization showing attack flow"""
    active_attacks = topology.get_active_attacks()
    
    if not active_attacks:
        return None
    
    data = []
    for attack in active_attacks:
        data.append({
            'From': attack['attacker_ip'],
            'To': attack['target_ip'],
            'Attack Type': attack['attack_type'],
            'Time': attack['timestamp'].strftime('%H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    return df


def create_attack_timeline(topology):
    """Create attack timeline visualization"""
    attacks = topology.attack_log
    
    if not attacks:
        return None
    
    # Count attacks over time
    attack_types = {}
    for attack in attacks:
        attack_type = attack['attack_type']
        if attack_type not in attack_types:
            attack_types[attack_type] = 0
        attack_types[attack_type] += 1
    
    df = pd.DataFrame({
        'Attack Type': list(attack_types.keys()),
        'Count': list(attack_types.values())
    }).sort_values('Count', ascending=True)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['Count'],
            y=df['Attack Type'],
            orientation='h',
            marker=dict(color='#FF6B6B', line=dict(color='white', width=2)),
            text=df['Count'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='🎯 Attacks by Type',
        xaxis_title='Number of Attacks',
        yaxis_title='Attack Type',
        hovermode='y unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig



def create_attack_matrix(topology):
    """Create attack source-target matrix"""
    attacks = topology.attack_log
    
    if not attacks:
        return None
    
    # Count attacks between devices
    from collections import defaultdict
    matrix = defaultdict(int)
    
    for attack in attacks:
        key = f"{attack['attacker_ip']} → {attack['target_ip']}"
        matrix[key] += 1
    
    df = pd.DataFrame({
        'Attack Path': list(matrix.keys()),
        'Attempts': list(matrix.values())
    }).sort_values('Attempts', ascending=False)
    
    return df


if __name__ == "__main__":
    # Test visualization
    topo = NetworkTopology(n_iot_devices=5, n_attackers=2)
    
    # Start some attacks
    attackers = topo.get_attackers()
    iot_devices = topo.get_iot_devices()
    
    for i in range(3):
        if i < len(attackers) and i < len(iot_devices):
            attack = topo.start_attack(
                attackers[i % len(attackers)].device_id,
                iot_devices[i % len(iot_devices)].device_id,
                f'Attack_{i}'
            )
    
    print("Testing visualization functions...")
    print("✓ Network topology created")
    print(f"✓ Devices: {topo.get_network_stats()['total_devices']}")
    print(f"✓ Active attacks: {len(topo.get_active_attacks())}")
