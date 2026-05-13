"""
Attack Detection Pipeline
Loads the trained model and provides prediction functions
"""

import pickle
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import os


class AttackDetectionPipeline:
    def __init__(self, model_path='xgboost_attack_detection_model.pkl',
                 scaler_path='scaler.pkl',
                 encoder_path='label_encoder.pkl',
                 info_path='model_info.json'):
        """Initialize the pipeline with trained model and artifacts"""
        
        self.model = None
        self.scaler = None
        self.encoder = None
        self.model_info = None
        self.feature_cols = None
        
        # Load model
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✓ Model loaded from {model_path}")
        else:
            print(f"✗ Model file not found: {model_path}")
            
        # Load scaler
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"✓ Scaler loaded from {scaler_path}")
        else:
            print(f"✗ Scaler file not found: {scaler_path}")
            
        # Load encoder
        if os.path.exists(encoder_path):
            with open(encoder_path, 'rb') as f:
                self.encoder = pickle.load(f)
            print(f"✓ Label encoder loaded from {encoder_path}")
        else:
            print(f"✗ Encoder file not found: {encoder_path}")
            
        # Load model info
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                self.model_info = json.load(f)
            print(f"✓ Model info loaded from {info_path}")
        else:
            print(f"✗ Model info file not found: {info_path}")
    
    def predict(self, X):
        """Make predictions on input data"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Scale the input
        X_scaled = X
        
        # Get predictions and probabilities
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Decode predictions
        pred_labels = self.encoder.inverse_transform(predictions)
        
        return {
            'predictions': predictions,
            'pred_labels': pred_labels,
            'probabilities': probabilities,
            'class_names': self.encoder.classes_
        }
    
    def predict_single(self, features):
        """Make prediction on a single sample"""
        if isinstance(features, dict):
            features = np.array(list(features.values())).reshape(1, -1)
        elif isinstance(features, list):
            features = np.array(features).reshape(1, -1)
        else:
            features = features.reshape(1, -1)
        
        result = self.predict(features)
        
        return {
            'prediction': result['pred_labels'][0],
            'prediction_id': result['predictions'][0],
            'probabilities': dict(zip(result['class_names'], result['probabilities'][0])),
            'confidence': float(np.max(result['probabilities'][0]))
        }
    
    def get_model_info(self):
        """Get model information"""
        return self.model_info
    
    def is_attack(self, features):
        """Check if features represent an attack"""
        result = self.predict_single(features)
        return result['prediction'] != 'Normal', result


if __name__ == "__main__":
    # Test the pipeline
    pipeline = AttackDetectionPipeline()
    
    if pipeline.model is not None:
        print("\n" + "="*60)
        print("Pipeline Test")
        print("="*60)
        
        # Create dummy features
        info = pipeline.get_model_info()
        if info:
            n_features = info['n_features']
            dummy_features = np.random.randn(5, n_features)
            
            result = pipeline.predict(dummy_features)
            print(f"\nTest predictions: {result['pred_labels']}")
            print(f"Confidences: {np.max(result['probabilities'], axis=1)}")
