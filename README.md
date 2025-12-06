# LLM-Powered Network Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node.js-20+-green.svg)](https://nodejs.org/)
[![Angular 18](https://img.shields.io/badge/angular-18-red.svg)](https://angular.io/)

A privacy-focused network packet analysis tool that runs entirely locally using Gemma 2 12B LLM via Ollama. Upload PCAPNG network capture files and get plain-English security analysis with actionable recommendations.

This application can take network logs, break them down, identify anomalies, and return the who, what, when, where, and why behind those anomalies. It also provides action plans that users can follow to resolve them. Everything runs locally, remains secure, and makes a complex task manageable for anyone. The UI is modern and intuitive.

![Network Analyzer Demo](docs/images/demo-screenshot.png)

## 🚀 Features

- **🔒 100% Local Processing** - All analysis happens on your machine, no data leaves your device
- **📁 PCAPNG File Support** - Analyzes pcapng and pcap network capture files using Scapy
- **🤖 AI-Powered Analysis** - Uses Gemma 2 12B for plain-English explanations and recommendations
- **⚡ Real-Time Progress** - WebSocket updates during analysis with live progress tracking
- **🎯 Smart Anomaly Detection** - Identifies 6 types of network anomalies:
  - Port scanning attacks
  - DDoS/SYN flood attacks
  - High retransmission rates
  - Connection failures and timeouts
  - Unusual port usage
  - Suspicious traffic patterns (data exfiltration, C2 beaconing)
- **💼 Professional UI** - Clean, intuitive interface with severity-coded results
- **📊 Export Functionality** - Download analysis reports as JSON

## 🏗️ Architecture

### Backend (Python FastAPI)
- **PCAPNG Parser** - Uses Scapy to parse pcapng/pcap network capture files
- **Anomaly Detector** - Statistical analysis with 6 detection types
- **LLM Client** - Ollama/Gemma 2 12B integration for natural language analysis
- **WebSocket API** - Real-time progress updates

### Frontend (Angular 18 + Material UI)
- **Upload Component** - Drag-and-drop pcapng file upload with validation
- **Results Component** - Severity-coded anomaly display with expandable details
- **Analysis Service** - WebSocket communication with backend

### LLM Integration
- **Model**: Gemma 2 12B via Ollama
- **Privacy**: 100% local inference, no external API calls
- **Prompt Engineering**: Optimized for network security analysis

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.10 or higher
- **Node.js** v20.14.0 or higher
- **Ollama** with Gemma 2 12B model
- **Git** for cloning the repository

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/P-Orion/LLM-Powered-Network-Analyzer.git
cd LLM-Powered-Network-Analyzer
```

### 2. One-Command Setup (Recommended)

Run the automated setup script:

**Windows:**
```bash
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

This will:
- ✅ Check all prerequisites
- ✅ Install Ollama and Gemma 2 12B model
- ✅ Set up Python virtual environment
- ✅ Install all dependencies (Python + Node.js)
- ✅ Start both backend and frontend servers
- ✅ Open your browser automatically

### 3. Manual Setup (Alternative)

If you prefer manual control:

#### Install Ollama and Gemma 2 12B

```bash
# Install Ollama from https://ollama.com/
# Or use the install script:
curl -fsSL https://ollama.com/install.sh | sh

# Pull Gemma 2 12B model
ollama pull gemma2:12b

# Verify installation
ollama list
```

#### Setup Backend

```bash
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

#### Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
```

#### Run the Application

**Terminal 1: Start Backend**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

**Terminal 2: Start Frontend**
```bash
cd frontend
ng serve
```

### 4. Access the Application

The application will be available at: **http://localhost:4200**

## 📖 Usage Guide

### 1. Upload a PCAPNG File
- Drag and drop a pcapng file onto the upload zone
- Or click to browse and select a file
- Supported formats: `.pcapng`, `.pcap`

### 2. Wait for Analysis
- Real-time progress updates will be shown
- Large files (>50MB) may take 2-5 minutes
- Very large files (>200MB) may take 5-15 minutes

### 3. Review Results
- Anomalies are sorted by severity (CRITICAL → HIGH → MEDIUM → LOW)
- Expand each anomaly card to see:
  - Detailed description
  - Specific evidence (IPs, ports, packet counts)
  - Why it matters (security/performance impact)
  - Recommended actions

### 4. Export Report
- Click "Export Report (JSON)" to download full analysis
- Save for later review or share with your team

## 🧪 Test Data

Generate test PCAPNG files with various network scenarios:

```bash
cd backend/tests
../venv/Scripts/python generate_test_pcapng.py
```

This creates:
- `test_port_scan.pcapng` - Port scanning attack (150 ports)
- `test_syn_flood.pcapng` - SYN flood DDoS attack (500 SYN packets)
- `test_normal_traffic.pcapng` - Normal legitimate traffic (100 connections)
- `test_retransmissions.pcapng` - Network performance issues (30% retransmission rate)
- `test_mixed_protocols.pcapng` - Mixed TCP/UDP/ICMP traffic

Use these pcapng files to test the application!

## 🔍 Anomaly Detection

The system detects 6 types of network anomalies:

### 1. Port Scanning
- **Detection**: >20 ports accessed from single source in 60 seconds
- **Severity**: CRITICAL
- **Example**: Attacker scanning for open services

### 2. SYN Floods (DDoS)
- **Detection**: SYN/ACK ratio > 3:1
- **Severity**: CRITICAL
- **Example**: Overwhelming server with connection requests

### 3. High Retransmissions
- **Detection**: >5% packet retransmission rate
- **Severity**: MEDIUM
- **Example**: Network congestion or faulty equipment

### 4. Connection Failures
- **Detection**: >10% RST packets or incomplete handshakes
- **Severity**: HIGH
- **Example**: Firewall blocks or service unavailability

### 5. Unusual Ports
- **Detection**: High traffic to non-standard ports (>10000)
- **Severity**: LOW-MEDIUM
- **Example**: Non-standard service or potential backdoor

### 6. Suspicious Patterns
- **Detection**: Large outbound transfers to external IPs
- **Severity**: HIGH
- **Example**: Data exfiltration or malware communication

## 🔒 Privacy & Security

### Privacy Guarantees
- ✅ All processing happens locally on your machine
- ✅ No external API calls (except to local Ollama instance)
- ✅ No data sent to cloud services
- ✅ You control all data retention
- ✅ Sensitive packet payloads are NOT stored

### Data Handling
- Log files are processed in memory
- Only metadata is extracted (IPs, ports, flags, timestamps)
- Full packet payloads are discarded
- Results can be exported or deleted at will

## ⚡ Performance

### Expected Processing Times

| File Size | Expected Time | Optimization |
|-----------|---------------|--------------|
| <10MB | 30s - 1min | Full analysis |
| 10-50MB | 1-2 minutes | Time-window chunking |
| 50-200MB | 2-5 minutes | Statistical pre-filtering |
| >200MB | 5-15 minutes | Aggressive pre-filtering |

### Optimization Strategy
- Statistical analysis filters out 70-80% of normal traffic
- Only suspicious patterns sent to LLM for detailed analysis
- Async processing with progress updates
- Streaming file reading (no full memory load)

## 🛠️ Development

### Project Structure

```
LLM-Powered-Network-Analyzer/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Python dependencies
│   ├── parsers/
│   │   └── log_parser.py          # PCAPNG file parser (Scapy)
│   ├── analyzers/
│   │   └── anomaly_detector.py    # Statistical anomaly detection
│   ├── llm/
│   │   └── gemma_client.py        # Ollama/Gemma integration
│   └── tests/
│       ├── generate_test_pcapng.py # Test data generator
│       └── *.pcapng               # Test files
│
├── frontend/
│   ├── src/app/
│   │   ├── app.component.*        # Main app component
│   │   ├── services/
│   │   │   └── analysis.service.ts  # WebSocket service
│   │   └── components/
│   │       ├── upload/            # File upload component
│   │       └── results/           # Results display component
│   ├── package.json
│   └── angular.json
│
├── docs/                          # Documentation
├── scripts/                       # Setup and utility scripts
├── README.md                      # This file
├── LICENSE                        # MIT License
└── .gitignore                     # Git ignore rules
```

### Backend Development

```bash
cd backend
venv\Scripts\activate

# Run with auto-reload
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Run with live reload
ng serve

# Build for production
ng build
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
ng test
```

## 🔧 API Documentation

### REST API

**GET** `/health`
- Health check endpoint
- Returns: `{"status": "healthy", "timestamp": "..."}`

**POST** `/api/upload`
- Upload file and get metadata
- Returns: File info, size, estimated processing time

**GET** `/api/test-llm`
- Test LLM connection status
- Returns: Connection status and model info

### WebSocket

**WS** `/ws/analyze`
- Real-time analysis with progress updates
- Receives: `{"content": "pcapng file content"}`
- Sends: Progress updates and final results

## 🐛 Troubleshooting

### Common Issues

**Backend Won't Start**
- `ollama: command not found` → Install Ollama from https://ollama.com/
- `Model not found: gemma2:12b` → Run `ollama pull gemma2:12b`
- `Port 8000 already in use` → Kill existing process or change port

**Frontend Won't Start**
- `ng: command not found` → Install Angular CLI: `npm install -g @angular/cli@18`
- `Port 4200 already in use` → Use `ng serve --port 4201`

**WebSocket Connection Issues**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

**LLM Analysis Issues**
- Check Ollama is running: `ollama list`
- Restart Ollama service if needed
- Verify Gemma model is fully downloaded

For more troubleshooting tips, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `npm test` and `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LLM**: Gemma 2 12B by Google (via Ollama)
- **Frontend**: Angular 18 + Angular Material
- **Backend**: Python FastAPI + Scapy
- **Inspiration**: Built for defense/security network analysis needs

## 📞 Support

For issues, questions, or feedback:

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review existing [GitHub Issues](https://github.com/P-Orion/LLM-Powered-Network-Analyzer/issues)
3. Create a new issue with detailed information
4. Test with provided sample PCAPNG files first

## 🎯 Roadmap

- [ ] PDF export for reports
- [ ] Historical analysis comparison
- [ ] Custom detection rule configuration
- [ ] Support for additional log formats (Snort, Suricata)
- [ ] Machine learning-based baseline learning
- [ ] Integration with SIEM platforms
- [ ] Multi-file batch analysis
- [ ] Real-time log streaming analysis

---

**Built with security and privacy in mind. Your data never leaves your machine.**

⭐ **Star this repository if you find it useful!**
