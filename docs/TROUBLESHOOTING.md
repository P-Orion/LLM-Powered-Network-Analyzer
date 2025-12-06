# Troubleshooting Guide

This guide helps you resolve common issues when setting up and using the LLM-Powered Network Analyzer.

## 🚀 Quick Fixes

### Application Won't Start
1. Run the setup script: `python setup.py`
2. Check all prerequisites are installed
3. Verify Ollama is running: `ollama list`
4. Check ports 4200 and 8000 are available

### Analysis Fails
1. Verify PCAPNG file is valid
2. Check file size (max 500MB recommended)
3. Ensure Gemma 2 12B model is downloaded
4. Check backend logs for errors

## 🔧 Installation Issues

### Python Issues

#### Error: `python: command not found`
**Solution:**
- **Windows**: Install Python from [python.org](https://python.org)
- **macOS**: Install via Homebrew: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11` or equivalent

#### Error: `Python version too old`
**Requirements:** Python 3.10 or higher
**Solution:**
```bash
# Check current version
python --version

# Install newer version
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

#### Error: `pip: command not found`
**Solution:**
```bash
# Windows
python -m ensurepip --upgrade

# macOS/Linux
python3 -m ensurepip --upgrade
```

#### Error: `Virtual environment creation failed`
**Solution:**
```bash
# Install venv module
python -m pip install virtualenv

# Create environment manually
python -m venv backend/venv

# Activate and install dependencies
# Windows:
backend\venv\Scripts\activate
# macOS/Linux:
source backend/venv/bin/activate

pip install -r backend/requirements.txt
```

### Node.js Issues

#### Error: `node: command not found`
**Solution:**
- Install Node.js 20+ from [nodejs.org](https://nodejs.org)
- Or use Node Version Manager (nvm)

#### Error: `npm: command not found`
**Solution:**
- Node.js installation should include npm
- Reinstall Node.js from official website

#### Error: `Angular CLI not found`
**Solution:**
```bash
# Install globally
npm install -g @angular/cli@18

# Or use npx
npx @angular/cli@18 serve
```

#### Error: `npm install fails with permission errors`
**Solution:**
```bash
# Fix npm permissions (macOS/Linux)
sudo chown -R $(whoami) ~/.npm

# Or use npx instead of global install
npx @angular/cli@18 serve
```

### Ollama Issues

#### Error: `ollama: command not found`
**Solution:**
1. Install Ollama from [ollama.com](https://ollama.com)
2. **Windows**: Download installer and run
3. **macOS/Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

#### Error: `Ollama service not running`
**Solution:**
```bash
# Start Ollama service
ollama serve

# Or restart the service
# Windows: Restart from Services app
# macOS: brew services restart ollama
# Linux: sudo systemctl restart ollama
```

#### Error: `Model not found: gemma2:12b`
**Solution:**
```bash
# Pull the model (requires internet)
ollama pull gemma2:12b

# Verify model is available
ollama list
```

#### Error: `Ollama connection refused`
**Solution:**
1. Check Ollama is running: `ollama list`
2. Verify port 11434 is not blocked
3. Restart Ollama service
4. Check firewall settings

## 🌐 Network and Port Issues

### Port Already in Use

#### Backend Port 8000
**Error:** `Port 8000 is already in use`
**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or change port in backend/main.py
uvicorn main:app --port 8001
```

#### Frontend Port 4200
**Error:** `Port 4200 is already in use`
**Solution:**
```bash
# Use different port
ng serve --port 4201

# Or kill existing process
# Windows:
netstat -ano | findstr :4200
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:4200 | xargs kill -9
```

### WebSocket Connection Issues

#### Error: `WebSocket connection failed`
**Symptoms:**
- Upload works but analysis doesn't start
- No progress updates shown
- Connection errors in browser console

**Solution:**
1. Ensure backend is running on port 8000
2. Check CORS settings in `backend/main.py`
3. Verify WebSocket endpoint: `ws://localhost:8000/ws/analyze`
4. Check browser developer tools for errors

#### Error: `CORS policy blocks request`
**Solution:**
Verify CORS configuration in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📁 File and Analysis Issues

### File Upload Issues

#### Error: `File format not supported`
**Supported formats:** `.pcapng`, `.pcap`
**Solution:**
1. Verify file extension
2. Convert other formats to PCAPNG using Wireshark
3. Check file is not corrupted

#### Error: `File too large`
**Limits:** 500MB recommended maximum
**Solution:**
1. Filter capture in Wireshark before export
2. Split large files into smaller chunks
3. Increase timeout in backend if needed

#### Error: `Invalid PCAPNG file`
**Solution:**
1. Open file in Wireshark to verify
2. Re-export from Wireshark as PCAPNG
3. Check file permissions
4. Ensure file is not corrupted

### Analysis Issues

#### Error: `Analysis timeout`
**Causes:**
- File too large
- LLM not responding
- Insufficient system resources

**Solution:**
1. Try smaller file first
2. Check Ollama is responding: `ollama list`
3. Restart Ollama service
4. Increase timeout in backend
5. Check system memory usage

#### Error: `No anomalies detected in clean traffic`
**Expected behavior:** Clean traffic should show few/no anomalies
**Solution:**
1. Use test files with known anomalies
2. Generate test data: `python backend/tests/generate_test_pcapng.py`
3. Verify detection thresholds in code

#### Error: `LLM returns invalid JSON`
**Solution:**
1. Check Gemma model is fully downloaded
2. Restart Ollama service
3. Check backend logs for parsing errors
4. Verify prompt engineering in `backend/llm/gemma_client.py`

## 🖥️ System-Specific Issues

### Windows Issues

#### Error: `'python' is not recognized`
**Solution:**
1. Add Python to PATH during installation
2. Use `py` instead of `python`
3. Reinstall Python with "Add to PATH" checked

#### Error: `Scripts execution policy`
**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Error: `Long path names not supported`
**Solution:**
1. Enable long paths in Windows
2. Use shorter directory names
3. Move project closer to root drive

### macOS Issues

#### Error: `Command line tools not installed`
**Solution:**
```bash
xcode-select --install
```

#### Error: `Permission denied`
**Solution:**
```bash
# Fix permissions
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

### Linux Issues

#### Error: `Package not found`
**Solution:**
```bash
# Update package lists
sudo apt update

# Install required packages
sudo apt install python3.11 python3.11-venv nodejs npm
```

#### Error: `Permission denied on port binding`
**Solution:**
```bash
# Use ports > 1024 (non-privileged)
# Or run with sudo (not recommended)
```

## 🔍 Debugging Tips

### Enable Debug Logging

#### Backend Debug Mode
Add to `backend/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Frontend Debug Mode
Open browser developer tools (F12) and check:
- Console tab for JavaScript errors
- Network tab for failed requests
- WebSocket frames for connection issues

### Check System Resources

#### Memory Usage
```bash
# Windows
tasklist /fi "imagename eq python.exe"

# macOS/Linux
ps aux | grep python
top -p $(pgrep python)
```

#### Disk Space
```bash
# Windows
dir C:\ /-c

# macOS/Linux
df -h
```

### Log File Locations

#### Backend Logs
- Console output when running `python main.py`
- Add file logging if needed

#### Frontend Logs
- Browser developer console
- Angular CLI output when running `ng serve`

#### Ollama Logs
```bash
# Check Ollama logs
ollama logs

# Or system logs
# Windows: Event Viewer
# macOS: Console app
# Linux: journalctl -u ollama
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing GitHub issues**
3. **Try with test data first**
4. **Check all prerequisites are met**
5. **Gather error messages and logs**

### Creating a Bug Report

Include:
1. **Operating system and version**
2. **Python version**: `python --version`
3. **Node.js version**: `node --version`
4. **Ollama version**: `ollama --version`
5. **Complete error message**
6. **Steps to reproduce**
7. **Log files or screenshots**

### Community Support

- **GitHub Issues**: [Create new issue](https://github.com/P-Orion/LLM-Powered-Network-Analyzer/issues)
- **GitHub Discussions**: For questions and community help
- **Documentation**: Check README.md and other docs

## 🔄 Reset and Clean Install

### Complete Reset
If all else fails, try a clean installation:

```bash
# 1. Remove existing installation
rm -rf backend/venv
rm -rf frontend/node_modules

# 2. Clean npm cache
npm cache clean --force

# 3. Run setup again
python setup.py
```

### Manual Clean Install
```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# 2. Frontend
cd ../frontend
npm install

# 3. Test Ollama
ollama pull gemma2:12b
ollama list
```

---

**Still having issues?** Create a [GitHub issue](https://github.com/P-Orion/LLM-Powered-Network-Analyzer/issues) with detailed information about your problem.