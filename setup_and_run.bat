@echo off
REM Quick Setup Script for Attack Detection System
REM This script installs all dependencies and starts the dashboard

echo.
echo ========================================================================
echo  SHIELD - Network Attack Detection System - SETUP
echo ========================================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ first
    pause
    exit /b 1
)

echo [1/3] Installing required packages...
pip install --upgrade pip >nul 2>&1
pip install -r requirements_streamlit.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo [2/3] Verifying model files...

if not exist "xgboost_attack_detection_model.pkl" (
    echo ERROR: Model file not found!
    echo Please train the model first using: jupyter notebook lstm_attack_timeseries.ipynb
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Attack Detection Dashboard...
echo.
echo ========================================================================
echo  STARTING STREAMLIT DASHBOARD
echo ========================================================================
echo.
echo Dashboard URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================================================
echo.

python -m streamlit run streamlit_app.py

pause
