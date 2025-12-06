# 🚀 Setup and Running Guide - Network Log Analyzer

## 🎯 Single Command Launch (Recommended)

### Windows:
```bash
python run.py
```
Or double-click `run.bat`

### macOS/Linux:
```bash
python3 run.py
```
Or run `./run.sh`

This **ONE COMMAND** will:
- ✅ Check all prerequisites automatically
- ✅ Create Python virtual environment
- ✅ Install all dependencies (Python + Node.js)
- ✅ Start both backend and frontend servers
- ✅ Open your browser automatically
- ✅ Handle all setup for you!

## Manual Setup (Alternative)

## 📋 Prerequisites

1. **Python 3.10+** - Download from [python.org](https://python.org)
2. **Node.js 20+** - Download from [nodejs.org](https://nodejs.org)
3. **Ollama** - Download from [ollama.com](https://ollama.com)

## 🔧 Step-by-Step Setup

### 1. Install Ollama and Gemma Model
```bash
# Download and install Ollama from https://ollama.com
# Then pull the Gemma 2 12B model:
ollama pull gemma2:12b

# Verify installation:
ollama list
```

### 2. Setup Backend (Python)
```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Frontend (Angular)
```bash
# Navigate to frontend folder
cd frontend

# Install Angular CLI globally (if not installed)
npm install -g @angular/cli

# Install dependencies
npm install
```

## ▶️ Running the Application

### Method 1: Use the Batch File (Windows)
```bash
# Simply double-click or run:
start.bat
```

### Method 2: Manual Start
Open **TWO** terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
ng serve
```

### 3. Access the Application
Open your browser and go to: **http://localhost:4200**

## 🧪 Generate Test Data

To create test PCAPNG files for testing:

```bash
cd backend/tests
..\venv\Scripts\python generate_test_pcapng.py
```

This creates 5 test files:
- `test_port_scan.pcapng` - Port scanning attack
- `test_syn_flood.pcapng` - SYN flood attack  
- `test_normal_traffic.pcapng` - Normal traffic
- `test_retransmissions.pcapng` - High retransmission scenario
- `test_mixed_protocols.pcapng` - Mixed TCP/UDP/ICMP traffic

## 📁 Using the Application

1. **Upload PCAPNG File**: Drag and drop a `.pcapng` or `.pcap` file
2. **Wait for Analysis**: Progress bar shows real-time status
3. **Review Results**: Anomalies are color-coded by severity
4. **Export Report**: Download JSON report of findings

## 🔍 Creating PCAPNG Files

### Using Wireshark:
1. Open Wireshark
2. Start packet capture
3. Stop capture when done
4. Save as `.pcapng` format

### Using tcpdump:
```bash
# Capture to PCAPNG file
sudo tcpdump -i eth0 -w capture.pcapng

# Convert existing pcap to pcapng
tcpdump -r old_file.pcap -w new_file.pcapng
```

## ❗ Troubleshooting

### Backend Won't Start
```bash
# Check if Ollama is running
ollama list

# If not installed:
# Download from https://ollama.com and install

# Pull the model:
ollama pull gemma2:12b
```

### Frontend Won't Start
```bash
# Install Angular CLI
npm install -g @angular/cli

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Backend (port 8000):
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Frontend (port 4200):
# Use different port
ng serve --port 4201
```

### PCAPNG File Issues
- **File too large**: Maximum 500MB supported
- **Invalid format**: Only `.pcapng` and `.pcap` files accepted
- **No packets**: File must contain network packets
- **Corrupted file**: Re-capture or use test files

## 🔧 Development Mode

### Backend Development:
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Frontend Development:
```bash
cd frontend
ng serve --port 4200
```

## 📊 System Requirements

- **RAM**: 8GB minimum (16GB recommended for large files)
- **Storage**: 2GB free space
- **CPU**: Multi-core recommended for LLM processing
- **OS**: Windows 10+, macOS 10.15+, or Linux

## 🆘 Getting Help

1. **Check logs**: Look at terminal output for error messages
2. **Verify prerequisites**: Ensure Python, Node.js, and Ollama are installed
3. **Test with sample data**: Use generated test PCAPNG files first
4. **Check file format**: Ensure you're uploading valid PCAPNG files

## 🎯 Quick Test

1. Run `start.bat`
2. Generate test data: `cd backend/tests && ..\venv\Scripts\python generate_test_pcapng.py`
3. Upload `test_port_scan.pcapng` to the web interface
4. Verify it detects port scanning anomaly

---

**🎉 You're ready to analyze network traffic for security anomalies!**