#!/bin/bash
# Quick Setup Script for Attack Detection System (Linux/Mac)
# This script installs all dependencies and starts the dashboard

echo ""
echo "========================================================================"
echo "  SHIELD - Network Attack Detection System - SETUP"
echo "========================================================================"
echo ""

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/3] Installing required packages..."
pip3 install --upgrade pip >/dev/null 2>&1
pip3 install -r requirements_streamlit.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo "[2/3] Verifying model files..."

if [ ! -f "xgboost_attack_detection_model.pkl" ]; then
    echo "ERROR: Model file not found!"
    echo "Please train the model first using: jupyter notebook lstm_attack_timeseries.ipynb"
    exit 1
fi

echo ""
echo "[3/3] Starting Attack Detection Dashboard..."
echo ""
echo "========================================================================"
echo "  STARTING STREAMLIT DASHBOARD"
echo "========================================================================"
echo ""
echo "Dashboard URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================================================"
echo ""

python3 -m streamlit run streamlit_app.py
