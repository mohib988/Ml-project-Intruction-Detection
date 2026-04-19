"""
Device Simulator
Simulates network traffic and attacks for testing the detection system
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random


class DeviceSimulator:
    """Simulates a network device with normal and attack traffic"""
    
    def __init__(self, n_features=100, noise_level=0.1):
        self.n_features = n_features
        self.noise_level = noise_level
        self.blocked_ips = set()
        self.traffic_history = []
        
        # Attack type patterns (simplified)
        self.attack_patterns = {
            'DDoS_HTTP_Flood_attack': self._create_ddos_pattern,
            'DDoS_TCP_SYN_Flood_attack': self._create_syn_pattern,
            'DDoS_UDP_Flood_attack': self._create_udp_pattern,
            'Port_Scanning_attack': self._create_port_scan_pattern,
            'SQL_injection_attack': self._create_sql_injection_pattern,
            'XSS_attack': self._create_xss_pattern,
            'Backdoor_attack': self._create_backdoor_pattern,
            'MITM_attack': self._create_mitm_pattern,
            'Normal': self._create_normal_pattern
        }
    
    def _create_normal_pattern(self, n_samples=1):
        """Generate normal traffic pattern"""
        return np.random.normal(loc=0.5, scale=0.2, size=(n_samples, self.n_features))
    
    def _create_ddos_pattern(self, n_samples=1):
        """Generate DDoS HTTP flood pattern"""
        pattern = np.random.normal(loc=0.8, scale=0.1, size=(n_samples, self.n_features))
        # High request rate
        pattern[:, :10] = np.clip(pattern[:, :10] + 0.5, 0, 1)
        return pattern
    
    def _create_syn_pattern(self, n_samples=1):
        """Generate TCP SYN flood pattern"""
        pattern = np.random.normal(loc=0.7, scale=0.15, size=(n_samples, self.n_features))
        # High SYN flags
        pattern[:, 10:20] = np.clip(pattern[:, 10:20] + 0.6, 0, 1)
        return pattern
    
    def _create_udp_pattern(self, n_samples=1):
        """Generate UDP flood pattern"""
        pattern = np.random.normal(loc=0.75, scale=0.12, size=(n_samples, self.n_features))
        # High UDP traffic
        pattern[:, 20:30] = np.clip(pattern[:, 20:30] + 0.5, 0, 1)
        return pattern
    
    def _create_port_scan_pattern(self, n_samples=1):
        """Generate port scanning pattern"""
        pattern = np.random.normal(loc=0.4, scale=0.2, size=(n_samples, self.n_features))
        # Many different ports
        pattern[:, 30:40] = np.linspace(0, 1, self.n_features)[:n_samples, np.newaxis]
        return pattern
    
    def _create_sql_injection_pattern(self, n_samples=1):
        """Generate SQL injection pattern"""
        pattern = np.random.normal(loc=0.5, scale=0.15, size=(n_samples, self.n_features))
        # Suspicious SQL patterns
        pattern[:, 40:50] = np.clip(pattern[:, 40:50] + 0.4, 0, 1)
        return pattern
    
    def _create_xss_pattern(self, n_samples=1):
        """Generate XSS attack pattern"""
        pattern = np.random.normal(loc=0.5, scale=0.15, size=(n_samples, self.n_features))
        # Script injection indicators
        pattern[:, 50:60] = np.clip(pattern[:, 50:60] + 0.5, 0, 1)
        return pattern
    
    def _create_backdoor_pattern(self, n_samples=1):
        """Generate backdoor pattern"""
        pattern = np.random.normal(loc=0.6, scale=0.15, size=(n_samples, self.n_features))
        # Suspicious command patterns
        pattern[:, 60:70] = np.clip(pattern[:, 60:70] + 0.5, 0, 1)
        return pattern
    
    def _create_mitm_pattern(self, n_samples=1):
        """Generate man-in-the-middle pattern"""
        pattern = np.random.normal(loc=0.55, scale=0.15, size=(n_samples, self.n_features))
        # Protocol anomalies
        pattern[:, 70:80] = np.clip(pattern[:, 70:80] + 0.4, 0, 1)
        return pattern
    
    def generate_traffic(self, attack_type='Normal', n_samples=1, src_ip=None):
        """Generate network traffic with specified attack type"""
        
        if src_ip is None:
            src_ip = f"192.168.1.{random.randint(1, 254)}"
        
        # Check if IP is blocked
        if src_ip in self.blocked_ips:
            return None, f"IP {src_ip} is blocked"
        
        # Generate features based on attack type
        if attack_type in self.attack_patterns:
            features = self.attack_patterns[attack_type](n_samples)
        else:
            features = self._create_normal_pattern(n_samples)
        
        # Add noise
        features = np.clip(features + np.random.normal(0, self.noise_level, features.shape), 0, 1)
        
        # Ensure correct shape
        features = np.clip(features, 0, 1)
        
        return features, src_ip
    
    def block_ip(self, ip_address):
        """Block an IP address"""
        if ip_address not in self.blocked_ips:
            self.blocked_ips.add(ip_address)
            return True
        return False
    
    def unblock_ip(self, ip_address):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            return True
        return False
    
    def get_blocked_ips(self):
        """Get list of all blocked IPs"""
        return list(self.blocked_ips)
    
    def clear_blocked_ips(self):
        """Clear all blocked IPs"""
        self.blocked_ips.clear()
    
    def add_to_history(self, traffic_record):
        """Add traffic to history"""
        self.traffic_history.append(traffic_record)
    
    def get_history(self):
        """Get traffic history"""
        return self.traffic_history
    
    def clear_history(self):
        """Clear traffic history"""
        self.traffic_history.clear()


if __name__ == "__main__":
    # Test the simulator
    simulator = DeviceSimulator(n_features=100)
    
    print("="*60)
    print("Device Simulator Test")
    print("="*60)
    
    # Generate different traffic types
    for attack_type in ['Normal', 'DDoS_HTTP_Flood_attack', 'Port_Scanning_attack']:
        features, src_ip = simulator.generate_traffic(attack_type, n_samples=1)
        if features is not None:
            print(f"\n{attack_type} (from {src_ip}):")
            print(f"  Shape: {features.shape}")
            print(f"  Mean: {features.mean():.4f}, Std: {features.std():.4f}")
    
    # Test IP blocking
    print(f"\n\nTesting IP Blocking:")
    print(f"Original IPs: {simulator.get_blocked_ips()}")
    simulator.block_ip("192.168.1.100")
    print(f"After blocking 192.168.1.100: {simulator.get_blocked_ips()}")
    simulator.unblock_ip("192.168.1.100")
    print(f"After unblocking: {simulator.get_blocked_ips()}")
