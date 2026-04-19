"""
Network Topology Management
Manages devices, network topology, and attack propagation
"""

import numpy as np
import pandas as pd
from datetime import datetime
import random


class NetworkDevice:
    """Represents a single network device"""
    
    def __init__(self, device_id, device_name, device_type, ip_address, x=None, y=None):
        """
        Initialize a network device
        
        Args:
            device_id: Unique identifier
            device_name: Display name (e.g., 'IoT_Sensor_01')
            device_type: 'iot', 'attacker', 'gateway', 'server'
            ip_address: IP address
            x, y: Network position coordinates
        """
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.ip_address = ip_address
        self.x = x or random.uniform(-10, 10)
        self.y = y or random.uniform(-10, 10)
        
        self.status = 'normal'  # 'normal', 'under_attack', 'attacked', 'compromised'
        self.is_active = True
        self.last_activity = datetime.now()
        self.attack_count = 0
        self.success_rate = 0.0
        self.data = {}
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.device_id,
            'name': self.device_name,
            'type': self.device_type,
            'ip': self.ip_address,
            'x': self.x,
            'y': self.y,
            'status': self.status,
            'active': self.is_active,
            'attack_count': self.attack_count
        }


class NetworkTopology:
    """Manages network topology and device relationships"""
    
    def __init__(self, n_iot_devices=5, n_attackers=2):
        """Initialize network topology"""
        self.devices = {}
        self.connections = []  # List of (source_id, target_id, type)
        self.attack_log = []
        
        # Create IoT Gateway (central point)
        gateway = NetworkDevice(
            device_id='gateway_001',
            device_name='IoT Gateway',
            device_type='gateway',
            ip_address='192.168.1.1',
            x=0, y=0
        )
        self.devices['gateway_001'] = gateway
        
        # Create IoT Devices in a circle
        for i in range(n_iot_devices):
            angle = (2 * np.pi * i) / n_iot_devices
            x = 5 * np.cos(angle)
            y = 5 * np.sin(angle)
            
            device = NetworkDevice(
                device_id=f'iot_{i+1:02d}',
                device_name=f'IoT Sensor {i+1}',
                device_type='iot',
                ip_address=f'192.168.1.{i+10}',
                x=x, y=y
            )
            self.devices[device.device_id] = device
            
            # Connect to gateway
            self.connections.append(('gateway_001', device.device_id, 'normal'))
        
        # Create Attackers (external)
        for i in range(n_attackers):
            angle = (2 * np.pi * i) / n_attackers
            x = -8 + random.uniform(-2, 2)
            y = 8 * np.sin(angle)
            
            device = NetworkDevice(
                device_id=f'attacker_{i+1:02d}',
                device_name=f'Attacker {i+1}',
                device_type='attacker',
                ip_address=f'203.0.113.{i+1}',
                x=x, y=y
            )
            self.devices[device.device_id] = device
        
        # Create Server
        server = NetworkDevice(
            device_id='server_001',
            device_name='Central Server',
            device_type='server',
            ip_address='192.168.1.100',
            x=0, y=-8
        )
        self.devices['server_001'] = server
        
        # Connect server to gateway
        self.connections.append(('gateway_001', 'server_001', 'normal'))
    
    def get_device(self, device_id):
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_all_devices(self):
        """Get all devices"""
        return list(self.devices.values())
    
    def get_iot_devices(self):
        """Get all IoT devices"""
        return [d for d in self.devices.values() if d.device_type == 'iot']
    
    def get_attackers(self):
        """Get all attacker devices"""
        return [d for d in self.devices.values() if d.device_type == 'attacker']
    
    def start_attack(self, attacker_id, target_id, attack_type):
        """Record an attack attempt"""
        timestamp = datetime.now()
        
        attacker = self.get_device(attacker_id)
        target = self.get_device(target_id)
        
        if not (attacker and target):
            return None
        
        # Log attack
        attack_record = {
            'timestamp': timestamp,
            'attacker_id': attacker_id,
            'attacker_ip': attacker.ip_address,
            'target_id': target_id,
            'target_ip': target.ip_address,
            'attack_type': attack_type,
            'status': 'active'
        }
        
        self.attack_log.append(attack_record)
        
        # Update device status
        target.status = 'under_attack'
        target.last_activity = timestamp
        target.attack_count += 1
        
        # Add connection
        self.connections.append((attacker_id, target_id, 'attack'))
        
        return attack_record
    
    def end_attack(self, attack_record, blocked=False):
        """End an attack"""
        attack_record['status'] = 'blocked' if blocked else 'failed'
        attack_record['end_time'] = datetime.now()
        
        target = self.get_device(attack_record['target_id'])
        if target:
            if blocked:
                target.status = 'attacked'
            else:
                target.status = 'normal'
    
    def block_device(self, device_id):
        """Block a device (add to firewall)"""
        device = self.get_device(device_id)
        if device:
            device.is_active = False
            device.status = 'blocked'
    
    def unblock_device(self, device_id):
        """Unblock a device"""
        device = self.get_device(device_id)
        if device:
            device.is_active = True
            device.status = 'normal'
    
    def get_network_stats(self):
        """Get network statistics"""
        devices = self.get_all_devices()
        iot_devices = self.get_iot_devices()
        
        under_attack = sum(1 for d in devices if d.status == 'under_attack')
        attacked = sum(1 for d in devices if d.status == 'attacked')
        compromised = sum(1 for d in devices if d.status == 'compromised')
        
        return {
            'total_devices': len(devices),
            'iot_devices': len(iot_devices),
            'under_attack': under_attack,
            'attacked': attacked,
            'compromised': compromised,
            'total_attacks': len(self.attack_log),
            'active_connections': len([c for c in self.connections if c[2] == 'attack'])
        }
    
    def get_active_attacks(self):
        """Get currently active attacks"""
        return [a for a in self.attack_log if a.get('status') == 'active']
    
    def get_network_graph_data(self):
        """Get network graph data for visualization"""
        nodes = []
        edges = []
        
        # Create nodes
        for device in self.devices.values():
            node_color = self._get_device_color(device)
            node_size = self._get_device_size(device)
            
            nodes.append({
                'id': device.device_id,
                'label': device.device_name,
                'x': device.x,
                'y': device.y,
                'color': node_color,
                'size': node_size,
                'device_type': device.device_type,
                'status': device.status,
                'ip': device.ip_address
            })
        
        # Create edges
        seen_edges = set()
        for src, tgt, edge_type in self.connections:
            edge_key = (src, tgt, edge_type)
            if edge_key not in seen_edges:
                edge_color = 'red' if edge_type == 'attack' else 'gray'
                edge_width = 3 if edge_type == 'attack' else 1
                
                edges.append({
                    'source': src,
                    'target': tgt,
                    'color': edge_color,
                    'width': edge_width,
                    'type': edge_type
                })
                seen_edges.add(edge_key)
        
        return {'nodes': nodes, 'edges': edges}
    
    def _get_device_color(self, device):
        """Get device color based on status"""
        if device.device_type == 'attacker':
            return '#FF6B6B' if not device.is_active else '#FF4444'
        elif device.device_type == 'iot':
            if device.status == 'under_attack':
                return '#FFD700'  # Gold
            elif device.status == 'attacked':
                return '#FFA500'  # Orange
            elif device.status == 'compromised':
                return '#DC143C'  # Crimson
            else:
                return '#4ECDC4'  # Teal
        elif device.device_type == 'gateway':
            return '#FFB533'
        elif device.device_type == 'server':
            return '#667EEA'
        else:
            return '#95E1D3'
    
    def _get_device_size(self, device):
        """Get device size based on type"""
        if device.device_type == 'gateway':
            return 60
        elif device.device_type == 'server':
            return 50
        elif device.device_type == 'attacker':
            return 40
        else:
            return 35
    
    def get_attack_stats_by_type(self):
        """Get attack statistics by type"""
        stats = {}
        for attack in self.attack_log:
            attack_type = attack['attack_type']
            if attack_type not in stats:
                stats[attack_type] = {'total': 0, 'blocked': 0}
            stats[attack_type]['total'] += 1
            if attack.get('status') == 'blocked':
                stats[attack_type]['blocked'] += 1
        return stats


if __name__ == "__main__":
    # Test network topology
    topo = NetworkTopology(n_iot_devices=5, n_attackers=2)
    
    print("="*60)
    print("Network Topology Test")
    print("="*60)
    
    print("\nDevices:")
    for device in topo.get_all_devices():
        print(f"  • {device.device_name} ({device.device_type}): {device.ip_address}")
    
    print("\nStarting attack...")
    attacker = topo.get_attackers()[0]
    target = topo.get_iot_devices()[0]
    
    attack = topo.start_attack(attacker.device_id, target.device_id, 'DDoS_HTTP_Flood_attack')
    print(f"  Attacker: {attacker.device_name}")
    print(f"  Target: {target.device_name}")
    
    print("\nNetwork Stats:")
    stats = topo.get_network_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    print("\nGraph Data Sample:")
    graph = topo.get_network_graph_data()
    print(f"  Nodes: {len(graph['nodes'])}")
    print(f"  Edges: {len(graph['edges'])}")
