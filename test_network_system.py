"""
Test Network Topology System
Tests network topology, visualization, and integration with pipeline
"""

import sys
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from network_topology import NetworkTopology, NetworkDevice
from network_visualization import (
    create_network_graph, create_device_status_table,
    create_attack_timeline, create_attack_matrix, 
    
)
from pipeline import AttackDetectionPipeline
from device_simulator import DeviceSimulator


def test_network_creation():
    """Test network topology creation"""
    print("\n" + "="*60)
    print("TEST 1: Network Topology Creation")
    print("="*60)
    
    try:
        topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        
        devices = topology.get_all_devices()
        print(f"✓ Created network with {len(devices)} devices")
        
        iot_devices = topology.get_iot_devices()
        print(f"✓ IoT Devices: {len(iot_devices)}")
        
        attackers = topology.get_attackers()
        print(f"✓ Attacker Devices: {len(attackers)}")
        
        print("\nDevice List:")
        for device in devices:
            print(f"  • {device.device_name:20} ({device.device_type:10}): {device.ip_address}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_attack_simulation():
    """Test attack simulation on network"""
    print("\n" + "="*60)
    print("TEST 2: Attack Simulation & Tracking")
    print("="*60)
    
    try:
        topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        
        attackers = topology.get_attackers()
        iot_devices = topology.get_iot_devices()
        
        # Simulate multiple attacks
        attacks = [
            (attackers[0].device_id, iot_devices[0].device_id, 'DDoS_HTTP_Flood_attack'),
            (attackers[0].device_id, iot_devices[1].device_id, 'Port_Scanning_attack'),
            (attackers[1].device_id, iot_devices[2].device_id, 'SQL_injection_attack'),
        ]
        
        for attacker_id, target_id, attack_type in attacks:
            attack = topology.start_attack(attacker_id, target_id, attack_type)
            print(f"✓ Attack initiated: {attack['attacker_ip']} → {attack['target_ip']}")
        
        active = topology.get_active_attacks()
        print(f"✓ Active attacks: {len(active)}")
        
        # End an attack
        topology.end_attack(attacks[0], blocked=True)
        print("✓ Attack blocked and ended")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_network_visualization():
    """Test graph visualization creation"""
    print("\n" + "="*60)
    print("TEST 3: Network Visualization")
    print("="*60)
    
    try:
        topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        
        # Simulate attacks
        attackers = topology.get_attackers()
        iot_devices = topology.get_iot_devices()
        topology.start_attack(attackers[0].device_id, iot_devices[0].device_id, 'DDoS_HTTP_Flood_attack')
        
        # Create graph data
        graph_data = topology.get_network_graph_data()
        print(f"✓ Graph nodes: {len(graph_data['nodes'])}")
        print(f"✓ Graph edges: {len(graph_data['edges'])}")
        
        # Create Plotly figure
        fig = create_network_graph(topology)
        print(f"✓ Plotly figure created: {type(fig).__name__}")
        
        # Create other visualizations
        timeline_fig = create_attack_timeline(topology)
        print(f"✓ Timeline figure created: {timeline_fig is not None}")
     
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_tables():
    """Test device status table generation"""
    print("\n" + "="*60)
    print("TEST 4: Device Status Tables")
    print("="*60)
    
    try:
        topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        
        # Create device status table
        df = create_device_status_table(topology)
        print(f"✓ Device table created: {len(df)} rows")
        print(f"✓ Columns: {', '.join(df.columns.tolist())}")
        
        # Create attack matrix
        attackers = topology.get_attackers()
        iot_devices = topology.get_iot_devices()
        topology.start_attack(attackers[0].device_id, iot_devices[0].device_id, 'DDoS_HTTP_Flood_attack')
        
        matrix = create_attack_matrix(topology)
        if matrix is not None:
            print(f"✓ Attack matrix created: {len(matrix)} attack paths")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_network_stats():
    """Test network statistics"""
    print("\n" + "="*60)
    print("TEST 5: Network Statistics")
    print("="*60)
    
    try:
        topology = NetworkTopology(n_iot_devices=5, n_attackers=2)
        
        # Initial stats
        stats = topology.get_network_stats()
        print(f"✓ Total devices: {stats['total_devices']}")
        print(f"✓ IoT devices: {stats['iot_devices']}")
        
        # After attack
        attackers = topology.get_attackers()
        iot_devices = topology.get_iot_devices()
        topology.start_attack(attackers[0].device_id, iot_devices[0].device_id, 'DDoS_HTTP_Flood_attack')
        
        stats = topology.get_network_stats()
        print(f"✓ Under attack: {stats['under_attack']}")
        print(f"✓ Total attacks: {stats['total_attacks']}")
        print(f"✓ Active connections: {stats['active_connections']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_integration_with_pipeline():
    """Test integration with ML pipeline"""
    print("\n" + "="*60)
    print("TEST 6: Integration with ML Pipeline")
    print("="*60)
    
    try:
        print("Loading Pipeline...")
        pipeline = AttackDetectionPipeline()
        print(f"✓ Pipeline loaded: {pipeline.is_loaded()}")
        
        print("Creating Simulator...")
        simulator = DeviceSimulator(n_features=pipeline.model_info['n_features'])
        print(f"✓ Simulator created with {pipeline.model_info['n_features']} features")
        
        print("Creating Network Topology...")
        topology = NetworkTopology()
        print(f"✓ Network topology created with {len(topology.get_all_devices())} devices")
        
        # Simulate attack traffic
        print("\nSimulating attack detection flow...")
        attackers = topology.get_attackers()
        iot_devices = topology.get_iot_devices()
        
        attacker = attackers[0]
        target = iot_devices[0]
        
        # Start network attack
        attack = topology.start_attack(attacker.device_id, target.device_id, 'DDoS_HTTP_Flood_attack')
        print(f"✓ Attack started: {attacker.device_name} → {target.device_name}")
        
        # Generate traffic
        features, src_ip = simulator.generate_traffic('DDoS_HTTP_Flood_attack', n_samples=1)
        print(f"✓ Traffic generated: {features.shape}")
        
        # Detect attack
        is_attack, result = pipeline.is_attack(features[0])
        print(f"✓ Detection result: {result['prediction']} (confidence: {result['confidence']*100:.1f}%)")
        
        if is_attack:
            topology.end_attack(attack, blocked=True)
            simulator.block_ip(attacker.ip_address)
            print(f"✓ Attack blocked: {attacker.ip_address} added to blocklist")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  NETWORK TOPOLOGY SYSTEM TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Network Creation", test_network_creation),
        ("Attack Simulation", test_attack_simulation),
        ("Visualization", test_network_visualization),
        ("Device Tables", test_device_tables),
        ("Network Stats", test_network_stats),
        ("Pipeline Integration", test_integration_with_pipeline),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
