"""
Device Simulator - Version 4
Stores transformed features in CSV, then samples from it
"""

import numpy as np
import pandas as pd
import random
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import pickle


class DeviceSimulator:
    """Generates real attack/normal traffic samples from pre-computed features CSV"""
    
    def __init__(self, dataset_path='Dataset', scaler_path='scaler.pkl', 
                 features_csv='transformed_features.csv', apply_scaling=True, regenerate=False):
        self.blocked_ips = set()
        self.traffic_history = []
        self.dataset_path = Path(dataset_path)
        self.features_csv_path = Path(features_csv)
        self.apply_scaling = apply_scaling
        self.scaler = None
        
        # Load pre-trained scaler
        if apply_scaling and Path(scaler_path).exists():
            try:
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"✓ Scaler loaded (expects {self.scaler.n_features_in_} features)")
            except Exception as e:
                print(f"⚠ Scaler loading error: {e}")
                self.scaler = StandardScaler()
        else:
            self.scaler = StandardScaler()
        
        # Features dataframe (loaded from CSV or generated)
        self.features_df = None
        self.n_features = 46
        
        # Config for cleaning
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
        
        # Load or generate features CSV
        if self.features_csv_path.exists() and not regenerate:
            print(f"✓ Loading features from {self.features_csv_path}")
            self.features_df = pd.read_csv(self.features_csv_path)
            print(f"  Features shape: {self.features_df.shape}")
        else:
            print("Generating features CSV from datasets...")
            self._generate_features_csv()
        self.features_df = pd.read_csv("device_simulator_data.csv")    
    
    def _convert_mixed(self, val):
        """Convert hex/numeric values"""
        if isinstance(val, str):
            val = val.strip()
            if val.startswith("0x"):
                try:
                    return int(val, 16)
                except:
                    return np.nan
            return pd.to_numeric(val, errors='coerce')
        return val
    
    def _clean_dataframe(self, df):
        """Apply EXACT same cleaning as LSTM notebook"""
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
        
        # ONE-HOT ENCODE (must be done on COMBINED data like notebook!)
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
    
    def _generate_features_csv(self):
        """Load, transform, and save all features to CSV (like LSTM notebook)"""
        print("Loading and combining all datasets...")
        
        dfs = []
        
        # Load all attack files (same as notebook)
        if self.dataset_path.exists():
            for csv_file in sorted(self.dataset_path.glob('*.csv')):
                attack_type = csv_file.stem
                try:
                    # Load a portion (notebook uses head(10000))
                    df = pd.read_csv(csv_file, low_memory=False, nrows=10000)
                    
                    # Add Attack_type if missing
                    if 'Attack_type' not in df.columns:
                        df['Attack_type'] = attack_type
                    
                    dfs.append(df)
                    print(f"  ✓ Loaded {attack_type}: {len(df)} rows")
                except Exception as e:
                    print(f"  ✗ Error loading {attack_type}: {e}")
        
        # Load normal class data
        normal_dir = self.dataset_path / 'NormalClass'
        if normal_dir.exists():
            normal_dfs = []
            for csv_file in sorted(normal_dir.glob('*.csv')):
                try:
                    df = pd.read_csv(csv_file, low_memory=False, nrows=50000)
                    df['Attack_type'] = 'Normal'
                    normal_dfs.append(df)
                    print(f"  ✓ Loaded NormalClass/{csv_file.name}: {len(df)} rows")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
            
            if normal_dfs:
                df_normal = pd.concat(normal_dfs, axis=0, ignore_index=True)
                dfs.append(df_normal)
        
        # Combine all
        if dfs:
            combined_df = pd.concat(dfs, axis=0, ignore_index=True)
            print(f"\nCombined dataset: {combined_df.shape}")
            
            # Clean and encode ONCE on the combined data (CRITICAL!)
            combined_df = self._clean_dataframe(combined_df)
            print(f"After cleaning/encoding: {combined_df.shape}")
            
            # Extract features
            exclude_cols = {'frame.time', 'ip.dst_host', 'Attack_type', 'Attack_label'}
            feature_cols = sorted([col for col in combined_df.columns if col not in exclude_cols])
            print(f"Feature columns: {len(feature_cols)}")
            
            # Create features dataframe with attack type
            features_df = combined_df[feature_cols + ['Attack_type']].copy()
            
            # Apply scaling if available
            if self.apply_scaling and self.scaler:
                try:
                    scaled_features = self.scaler.transform(features_df[feature_cols].values)
                    for i, col in enumerate(feature_cols):
                        features_df[col] = scaled_features[:, i]
                    print("✓ Features scaled")
                except Exception as e:
                    print(f"⚠ Scaling error: {e}")
            
            # Save to CSV
            features_df.to_csv(self.features_csv_path, index=False)
            print(f"\n✓ Features saved to {self.features_csv_path}")
            print(f"  Shape: {features_df.shape}")
            
            # Load into memory
            self.features_df = features_df
        else:
            print("✗ No datasets loaded!")
    
    def generate_traffic(self, attack_type='Normal', src_ip=None,n_samples=1):

        if src_ip is None:
            src_ip = f"192.168.1.{random.randint(1, 254)}"

        # Check blocked IP
        if src_ip in self.blocked_ips:
            return None, f"IP {src_ip} is blocked"

        if self.features_df is None or self.features_df.empty:
            return None, "No features data loaded"

        # Filter rows by attack type
        df_filtered = self.features_df[
            self.features_df['Attack_type'] == attack_type
        ]

        if df_filtered.empty:
            print(f"⚠ No samples for {attack_type}")
            return None, "Attack type not found"

        # Pick ONE random row
        random_row = df_filtered.sample(n=1).iloc[0]

        # Remove Attack_type column
        features = random_row.drop('Attack_type')

        # Convert to numpy float32 array
        features = features.fillna(0).astype('float32').values
        print(features)

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
    print("Device Simulator Test - Combined Dataset Mode")
    print("="*60)
    
    simulator = DeviceSimulator()
    
    # Test different attack types (use correct names from CSV)
    test_types = ['Normal', 'DDoS_HTTP', 'Port_Scanning', 'SQL_injection']
    
    for attack_type in test_types:
        print(f"\nTesting {attack_type}:")
        for i in range(2):
            features, src_ip = simulator.generate_traffic(attack_type, n_samples=1)
            if features is not None:
                print(f"  Sample {i+1}: shape={features.shape}, first 5={features[0,:5]}")
            else:
                print(f"  Sample {i+1}: Error - {src_ip}")
