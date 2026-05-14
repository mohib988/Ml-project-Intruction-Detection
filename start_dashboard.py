"""
Quick Start Script - Attack Detection System
Run this to start the Streamlit dashboard
"""

import os
import sys
import subprocess

def main():
    print("="*70)
    print("🛡️  ATTACK DETECTION SYSTEM - QUICK START")
    print("="*70)
    
    # Check Python version
    print("\n✓ Checking Python version...")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required. Current: {}.{}".format(
            sys.version_info.major, sys.version_info.minor))
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if model files exist
    print("\n✓ Checking model files...")
    required_files = [
        'xgboost_attack_detection_model.pkl',
        'scaler.pkl',
        'label_encoder.pkl',
        'model_info.json'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing_files.append(file)
    

    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'plotly': 'plotly'
    }
    
    missing_packages = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NOT INSTALLED")
            missing_packages.append(package_name)
    
    if missing_packages:
        print("\n⚠️  Installing missing packages...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_streamlit.txt'
        ])
    

    print("\n📱 Dashboard will open at: http://localhost:8501")

    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard closed")
        sys.exit(0)


if __name__ == "__main__":
    main()
