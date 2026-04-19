# 🛡️ SHIELD - Quick Reference Guide
## Essential Commands & Workflows

---

## ⚡ Quick Start in 60 Seconds

### Windows
```batch
cd d:\advanceMlProject
setup_and_run.bat
```

### Linux/Mac
```bash
cd /path/to/advanceMlProject
chmod +x setup_and_run.sh
./setup_and_run.sh
```

**Then**: Open browser to `http://localhost:8501` ✅

---

## 📋 Common Commands

### Start Dashboard

**Option 1** (Easiest):
```bash
setup_and_run.bat              # Windows
./setup_and_run.sh             # Linux/Mac
```

**Option 2** (Direct):
```bash
streamlit run streamlit_app.py
```

**Option 3** (Custom port):
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Install Dependencies

**All at once**:
```bash
pip install -r requirements_streamlit.txt
```

**Individual**:
```bash
pip install streamlit pandas numpy scikit-learn xgboost plotly
```

### Test System

```bash
python test_system.py
```

**Expected Output**:
```
✓ PASSED: Pipeline
✓ PASSED: Simulator
✓ PASSED: Integration
✅ All tests passed
```

### Train Model

```bash
jupyter notebook lstm_attack_timeseries.ipynb
```

### Check Python Version

```bash
python --version              # Windows
python3 --version             # Linux/Mac
```

### Check Installed Packages

```bash
pip list | grep -E "streamlit|xgboost|plotly"
```

---

## 🎮 Using the Dashboard

### Simulate Attack

1. **Select attack type**: Dropdown in sidebar
2. **Set packets**: Slider (1-10)
3. **Set speed**: Slider (1-20 packets/sec)
4. **Click**: "▶️ Start Simulation"
5. **View**: Results in real-time

### Block IP

1. **Method 1**: Click "🚫 Block IP" button on detected attack
2. **Method 2**: Enter IP manually in IP Blocker tab
3. **Verify**: Check blocked IPs list

### View History

1. Navigate to: "📜 History" tab
2. Apply filters: By attack type or IP
3. Download: Click "📥 Download as CSV"

### Export Report

```
1. Go to: History tab
2. Set filters (optional)
3. Click: "📥 Download History as CSV"
4. Open: In Excel/Sheets
5. Analyze: Custom analysis
```

---

## 🔧 Troubleshooting Quick Fixes

### Problem: "Module not found"

```bash
# Solution 1: Install missing module
pip install xgboost

# Solution 2: Upgrade all
pip install --upgrade -r requirements_streamlit.txt

# Solution 3: Fresh install
pip uninstall -y xgboost plotly streamlit
pip install -r requirements_streamlit.txt
```

### Problem: Port 8501 in use

```bash
# Solution 1: Use different port
streamlit run streamlit_app.py --server.port 8502

# Solution 2: Kill process using port
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8501
kill -9 <PID>
```

### Problem: Model not found

```bash
# Verify files exist:
dir xgboost*.pkl              # Windows
ls xgboost*.pkl               # Linux/Mac

# If missing, train model:
jupyter notebook lstm_attack_timeseries.ipynb
```

### Problem: Streamlit not responding

```bash
# Restart dashboard:
# Ctrl+C in terminal
# Remove cache:
rm -rf .streamlit             # Linux/Mac
rmdir /s .streamlit           # Windows

# Run again:
streamlit run streamlit_app.py
```

### Problem: Out of memory

```bash
# Reduce data:
- Decrease packets per traffic
- Close other apps
- Increase RAM

# Or run on better system
```

---

## 📊 Dashboard Tabs Overview

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| 🎯 Real-time Monitor | Live detection | Start simulation, view alerts, block IPs |
| 📊 Statistics | Analyze data | Attack distribution, timeline, confidence |
| 🚫 IP Blocker | Manage IPs | View blocked, add/remove, statistics |
| 📜 History | Audit trail | View all events, filter, export CSV |

---

## 🎯 Common Workflows

### Workflow 1: Quick Attack Simulation

```
1. Open dashboard
2. Select "DDoS_HTTP_Flood_attack"
3. Set packets = 5
4. Click "Start Simulation"
5. Review results
6. View statistics
```

### Workflow 2: Test All Attack Types

```
Attacks to test:
- Normal (baseline)
- DDoS_HTTP_Flood_attack
- DDoS_TCP_SYN_Flood_attack
- DDoS_UDP_Flood_attack
- Port_Scanning_attack
- SQL_injection_attack
- XSS_attack
- Backdoor_attack
- MITM_attack

For each:
1. Select attack type
2. Generate 3-5 packets
3. Review confidence scores
4. Note detection accuracy
```

### Workflow 3: Generate Report

```
1. Run simulations (various types)
2. Let dashboard collect history
3. Go to History tab
4. Download CSV with all events
5. Open in Excel/Sheets
6. Create pivot tables & charts
7. Analyze patterns
8. Export as presentation
```

### Workflow 4: Monitor in Real-time

```
1. Enable auto-packet generation
2. Set speed to 10 packets/sec
3. Monitor dashboard continuously
4. Watch for patterns
5. Manually block suspicious IPs
6. Review statistics tab for insights
```

---

## 📈 Testing Attack Pattern Recognition

### DDoS HTTP Flood
- Expected: High confidence (>90%)
- Pattern: High request rates, similar traffic
- Block: Immediate IP block on detection

### Port Scanning
- Expected: High confidence (85%+)
- Pattern: Sequential port access
- Block: Early warning system

### SQL Injection
- Expected: Medium-High confidence (80%+)
- Pattern: SQL syntax in payloads
- Block: Database protection

### XSS Attack
- Expected: Medium confidence (80%+)
- Pattern: Script tags, JavaScript
- Block: Prevent script execution

---

## 🔒 Security Best Practices

### When Using Locally

✅ **DO:**
- Run on localhost only
- Use firewall restrictions
- Regularly review blocked IPs
- Export and archive logs
- Update dependencies monthly

❌ **DON'T:**
- Expose to internet
- Use default credentials
- Ignore warnings
- Skip security updates
- Share model files publicly

### Managing Blocked IPs

```
Good practice:
1. Review blocked list weekly
2. Remove false positives
3. Archive important blocks
4. Document reasons
5. Share with team

Bad practice:
- Never review
- Keep infinite blocks
- No backup
- Shared password
```

---

## 📞 Getting Help

### Check System Status

```bash
# Verify installation
python -c "from pipeline import AttackDetectionPipeline; print('✓ Pipeline OK')"
python -c "from device_simulator import DeviceSimulator; print('✓ Simulator OK')"

# Check versions
python -c "import xgboost; print('XGBoost:', xgboost.__version__)"
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
```

### Enable Debug Mode

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### View Logs

Check `.streamlit/logs/` directory for debug information

### Test Individual Components

```bash
# Test pipeline only
python -c "from pipeline import AttackDetectionPipeline; p = AttackDetectionPipeline()"

# Test simulator only
python -c "from device_simulator import DeviceSimulator; s = DeviceSimulator()"
```

---

## 💡 Tips & Tricks

### Performance Optimization

```
Fast Simulation:
- Speed: 20 packets/sec
- Packets: 1
- Display: Statistics only

Detailed Analysis:
- Speed: 5 packets/sec
- Packets: 10
- Display: Every result

Bulk Testing:
- Speed: 1 packet/sec
- Packets: 50+
- Auto-generate: ON
```

### Dashboard Shortcuts

```
Keyboard shortcuts:
- R: Rerun
- Ctrl+C: Stop (terminal)
- F5: Refresh page
- Ctrl+L: View logs (browser console)
```

### Data Analysis Tips

```
With History CSV:
1. Open in Excel
2. Create pivot table
3. Summarize by attack type
4. Calculate detection rate
5. Identify patterns
6. Export charts
```

---

## 🎓 Learning Path

### Day 1: Basics
- [ ] Install system
- [ ] Run dashboard
- [ ] Test Normal traffic
- [ ] View statistics

### Day 2: Attacks
- [ ] Test each attack type
- [ ] Observe confidence scores
- [ ] Block suspicious IPs
- [ ] Review history

### Day 3: Advanced
- [ ] Generate reports
- [ ] Analyze patterns  
- [ ] Understand confidence
- [ ] Customize settings

### Day 4+: Production
- [ ] Deploy dashboard
- [ ] Monitor in real-time
- [ ] Create alerts
- [ ] Integrate with systems

---

## 📅 Maintenance Checklist

### Weekly
- [ ] Review blocked IPs
- [ ] Check detection accuracy
- [ ] Backup history
- [ ] Update logs

### Monthly
- [ ] Update dependencies
- [ ] Review statistics
- [ ] Clean cache
- [ ] Archive old history

### Quarterly
- [ ] Retrain model (if needed)
- [ ] Security audit
- [ ] Performance review
- [ ] Update documentation

---

## 🚀 Performance Tips

### Make It Faster

```
Slow Dashboard?
1. Close other tabs
2. Reduce animation (developer tools)
3. Use faster simulation speed
4. Reduce packets
5. Clear browser cache
```

### Make It Stable

```
Unstable?
1. Restart dashboard
2. Clear .streamlit cache
3. Update packages
4. Check system resources
5. Restart computer
```

---

## 📞 Quick Help Matrix

| Issue | Quick Fix | Also Try |
|-------|-----------|----------|
| Streamlit not found | `pip install streamlit` | Clear pip cache |
| Port in use | Use `--server.port 8502` | Kill old process |
| Slow dashboard | Reduce packets/speed | Close other apps |
| Model not loading | Check file exists | Retrain model |
| Dashboard crashes | Restart app | Clear cache |
| High memory usage | Reduce history | Restart system |

---

## 🔗 Useful Links

```
Documentation:
- README_STREAMLIT.md          Overview & features
- COMPLETE_SETUP_GUIDE.md      Detailed setup
- ARCHITECTURE.md              System design
- (This file)                  Quick reference

Official Docs:
- https://docs.streamlit.io
- https://xgboost.readthedocs.io
- https://plotly.com/python
```

---

## 📝 Logging & Debugging

### View Application Logs

```bash
# Windows
type .streamlit\logs\<date>.log

# Linux/Mac
cat .streamlit/logs/<date>.log
```

### Enable Debugging

```python
# Add to streamlit_app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Export Logs

```bash
# Copy logs to file
cp .streamlit/logs/*.log logs_backup.txt
```

---

## 🎯 Next Steps

1. **Start Dashboard**: `streamlit run streamlit_app.py`
2. **Run Simulation**: Select attack type, click start
3. **View Results**: Monitor dashboard tabs
4. **Block Threats**: Click block button
5. **Export Report**: Download history CSV
6. **Analyze Data**: Review patterns
7. **Optimize**: Fine-tune detection

---

## ✅ Verification Checklist

Before going live:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Model files present (4 files)
- [ ] Test suite passes
- [ ] Dashboard runs without errors
- [ ] Simulations generate correctly
- [ ] IP blocking works
- [ ] History logs correctly
- [ ] Exports work properly
- [ ] Performance acceptable

---

## 📞 Emergency Contacts

**System Won't Start:**
1. Check Python: `python --version`
2. Check files: `dir xgboost*`
3. Check port: `netstat -ano | findstr 8501`
4. Restart terminal
5. Reinstall packages

**Dashboard Frozen:**
1. Press Ctrl+C in terminal
2. Wait 5 seconds
3. Restart: `streamlit run streamlit_app.py`

**Lost Data:**
1. Check history tab
2. Export what you can
3. Clear session state
4. Start fresh simulation

---

**Last Updated**: April 18, 2026
**Version**: 1.0.0
**Status**: Ready to Use ✅

