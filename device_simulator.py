"""
Device Simulator - Version 2
Simulates network traffic and attacks using EXACT feature engineering from LSTM notebook
Outputs exactly 46 features to match the XGBoost model
"""

import numpy as np
import pandas as pd
import random
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import pickle


class DeviceSimulator:
    """Generates real attack/normal traffic samples with proper feature engineering"""
    
    def __init__(self, dataset_path='Dataset', scaler_path='scaler.pkl', apply_scaling=True):
        self.blocked_ips = set()
        self.traffic_history = []
        self.dataset_path = Path(dataset_path)
        self.apply_scaling = apply_scaling
        self.scaler = None
        
        # Load pre-trained scaler
        if apply_scaling and Path(scaler_path).exists():
            try:
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"✓ Scaler loaded from {scaler_path}")
            except:
                print(f"⚠ Creating new scaler (file not available)")
                self.scaler = StandardScaler()
        else:
            self.scaler = StandardScaler()
        
        # Datasets cache
        self.datasets = {}
        self.dataset_files = {}
        self.n_features = 46  # Model expects exactly 46 features
        
        # Index datasets
        self._index_datasets()
        
        # Cleaning config (EXACT from LSTM notebook)
        self.drop_columns = [
            'ip.src_host', 'arp.src.proto_ipv4', 'arp.dst.proto_ipv4',
            'http.file_data', 'http.request.full_uri', 'icmp.transmit_timestamp',
            'http.request.uri.query', 'tcp.options', 'tcp.payload',
            'mqtt.msg', 'http.referer', 'http.request.version', 
            'tcp.srcport', 'dns.qry.name', 'mqtt.topic', 'mqtt.protoname'
        ]
        
        self.numeric_cols = [
            'icmp.seq_le', 'tcp.ack_raw', 'tcp.connection.fin', 'tcp.len',
            'tcp.dstport', 'arp.hw.size', 'udp.port', 'mqtt.conack.flags',
            'mqtt.conflags', 'mqtt.hdrflags', 'tcp.flags', 'icmp.checksum', 'tcp.checksum'
        ]
    
    def _index_datasets(self):
        """Index available datasets without loading"""
        if not self.dataset_path.exists():
            print(f"⚠ Dataset path not found: {self.dataset_path}")
            return
        
        # Attack datasets
        for csv_file in sorted(self.dataset_path.glob('*.csv')):
            attack_type = csv_file.stem.replace('_attack', '')
            self.dataset_files[attack_type] = csv_file
            print(f"  Dataset: {attack_type}")
        
        # Normal traffic
        normal_dir = self.dataset_path / 'NormalClass'
        if normal_dir.exists():
            normal_files = sorted(list(normal_dir.glob('*.csv')))
            if normal_files:
                self.dataset_files['Normal'] = normal_files
                print(f"  Dataset: Normal ({len(normal_files)} files)")
    
    def _convert_mixed(self, val):
        """Convert hex/numeric values (from LSTM notebook)"""
        if isinstance(val, str):
            val = val.strip()
            if val.startswith("0x"):
                try:
                    return int(val, 16)
                except:
                    return np.nan
            return pd.to_numeric(val, errors='coerce')
        return val
    
    def _clean_and_engineer(self, df):
       
        # Drop duplicates
        df = df.drop_duplicates(keep='first')
        
        # Drop unwanted columns
        drop_cols = [col for col in self.drop_columns if col in df.columns]
        df = df.drop(columns=drop_cols, errors='ignore')
        
        # Convert numeric columns
        for col in self.numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(self._convert_mixed)
        
        # Remove single-value columns
        single_val = []
        for col in df.columns:
            if df[col].nunique() == 1 and col not in ['Attack_type', 'Attack_label']:
                single_val.append(col)
        df = df.drop(columns=single_val, errors='ignore')
        
        # Parse datetime
        if 'frame.time' in df.columns:
            df['frame.time'] = pd.to_datetime(df['frame.time'], errors='coerce')
        
        # ONE-HOT ENCODE CATEGORICAL COLUMNS (CRITICAL!)
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        exclude = {'frame.time', 'ip.dst_host', 'Attack_type', 'Attack_label'}
        cat_cols = [col for col in cat_cols if col not in exclude]
        
        for col in cat_cols:
            try:
                dummies = pd.get_dummies(df[col], prefix=col, dummy_na=False)
                df = pd.concat([df, dummies], axis=1)
                df = df.drop(col, axis=1)
            except:
                pass
        
        return df
    
    def _extract_features(self, df):
        """Extract feature vectors from cleaned dataframe"""
        # Exclude metadata columns
        exclude_cols = {'frame.time', 'ip.dst_host', 'Attack_type', 'Attack_label'}
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Get numeric features
        df_features = df[feature_cols].fillna(0).astype('float32')
        
        return df_features.values, feature_cols
    
    def _load_dataset(self, attack_type, sample_rows=1):
        """Lazy load and clean dataset"""
        if attack_type in self.datasets:
            return self.datasets[attack_type]
        
        if attack_type not in self.dataset_files:
            return None
        print("---------------mohib------------")
        print(attack_type)
        print(self.dataset_files)
        print("---------------mohib------------s")
        try:
            if attack_type == 'Normal':
                dfs = []
                for csv_file in self.dataset_files['Normal']:
                    df = pd.read_csv(csv_file, low_memory=False, nrows=sample_rows)
                    dfs.append(df)
                df = pd.concat(dfs, ignore_index=True)
            else:
                csv_file = self.dataset_files[attack_type]
                df = pd.read_csv(csv_file, low_memory=False, nrows=sample_rows)
            
            # Clean and engineer
            print(df)
            df = self._clean_and_engineer(df)
            
            # Cache
            self.datasets[attack_type] = df
            features, cols = self._extract_features(df)
            print(f"✓ {attack_type}: {df.shape[0]} rows, {features.shape[1]} features")
            
            return df
            
        except Exception as e:
            print(f"✗ Error loading {attack_type}: {e}")
            return None
    
    def _get_data_pattern(self, attack_type, n_samples=1):
        """Get random samples from dataset with proper feature extraction"""
        df = self._load_dataset(attack_type)
        
        if df is None or df.empty:
            # Fallback
            print(f"⚠ Using fallback for {attack_type}")
            return np.random.randn(n_samples, self.n_features) * 0.5
        
        # Sample rows
        try:
            if len(df) >= n_samples:
                sampled = df.sample(n=n_samples, replace=False, random_state=None)
            else:
                sampled = df.sample(n=n_samples, replace=True, random_state=None)
        except:
            sampled = df.iloc[:min(n_samples, len(df))]
        
        # Extract features
        features, _ = self._extract_features(sampled)
        
        # Handle feature count mismatch
        if features.shape[1] != self.n_features:
            # Pad or trim to 46 features
            if features.shape[1] < self.n_features:
                padding = np.zeros((features.shape[0], self.n_features - features.shape[1]))
                features = np.hstack([features, padding])
            else:
                features = features[:, :self.n_features]
        
        # Scale using loaded scaler
        if self.apply_scaling and self.scaler:
            try:
                features = self.scaler.transform(features)
            except:
                pass
        
        return features
    
    def generate_traffic(self, attack_type='Normal', n_samples=1, src_ip=None):
        self._load_dataset( attack_type, sample_rows=n_samples)  # Ensure dataset is loaded
        """Generate traffic samples"""
        if src_ip is None:
            src_ip = f"192.168.1.{random.randint(1, 254)}"
        
        # Check if blocked
        if src_ip in self.blocked_ips:
            return None, f"IP {src_ip} is blocked"
        
        # Generate based on type
        if attack_type in self.dataset_files or attack_type == 'Normal':
            features = self._get_data_pattern(attack_type, n_samples)
        else:
            features = self._get_data_pattern('Normal', n_samples)
        
        # Ensure shape
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        return features, src_ip
    
    def block_ip(self, ip_address):
        """Block an IP"""
        if ip_address not in self.blocked_ips:
            self.blocked_ips.add(ip_address)
            return True
        return False
    
    def unblock_ip(self, ip_address):
        """Unblock an IP"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            return True
        return False
    
    def get_blocked_ips(self):
        """Get all blocked IPs"""
        return list(self.blocked_ips)
    
    def clear_blocked_ips(self):
        """Clear all blocked IPs"""
        self.blocked_ips.clear()
    
    def add_to_history(self, record):
        """Add to history"""
        self.traffic_history.append(record)
    
    def get_history(self):
        """Get history"""
        return self.traffic_history
    
    def clear_history(self):
        """Clear history"""
        self.traffic_history.clear()


if __name__ == "__main__":
    print("="*60)
    print("Device Simulator Test - 46-Feature Mode")
    print("="*60)
    
    simulator = DeviceSimulator()
    
    # Test different attack types
    test_types = ['Normal', 'DDoS_HTTP_Flood_attack', 'Port_Scanning_attack', 'SQL_injection_attack']
    
    for attack_type in test_types:
        if attack_type in simulator.dataset_files:
            features, src_ip = simulator.generate_traffic(attack_type, n_samples=2)
            if features is not None:
                print(f"\n{attack_type} (from {src_ip}):")
                print(f"  Shape: {features.shape}")
                print(f"  Min: {features.min():.4f}, Max: {features.max():.4f}")
                print(f"  Mean: {features.mean():.4f}, Std: {features.std():.4f}")
