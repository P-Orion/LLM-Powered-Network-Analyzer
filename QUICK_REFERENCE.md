# Quick Reference Guide - LLM Private Log Anomaly Finder

## 🎯 Project Goal
Build a localhost:4200 web app that analyzes PCAPNG network capture files using local Gemma 2 12B LLM to detect anomalies with plain-English explanations.

---

## ⚡ Quick Command Reference

### Initial Setup
```bash
# Install Ollama & Gemma
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:12b

# Backend dependencies
pip install fastapi uvicorn ollama websockets python-multipart aiofiles scapy

# Frontend setup
npm install -g @angular/cli
ng new log-analyzer --routing --style=scss
cd log-analyzer && npm install
```

### Running the Application
```bash
# Terminal 1 - Backend (port 8000)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend (port 4200)
cd frontend
ng serve --port 4200

# Access at: http://localhost:4200
```

---

## 📁 Project Structure

```
log-analyzer/
├── backend/
│   ├── main.py                    # FastAPI app, endpoints, WebSocket
│   ├── parsers/
│   │   └── log_parser.py          # Parse PCAPNG files using Scapy
│   ├── analyzers/
│   │   └── anomaly_detector.py    # Statistical anomaly detection
│   ├── llm/
│   │   └── gemma_client.py        # Ollama/Gemma integration
│   └── tests/
│       └── generate_test_pcapng.py  # Create test PCAPNG data
│
└── frontend/
    └── src/app/
        ├── components/
        │   ├── upload/            # File upload component
        │   └── results/           # Results display component
        └── services/
            └── analysis.service.ts # WebSocket service
```

---

## 🔍 TCP Anomalies to Detect

| Anomaly Type | Detection Method | Severity |
|--------------|------------------|----------|
| **Port Scanning** | >20 ports in 60s from one IP | CRITICAL |
| **SYN Flood** | SYN/ACK ratio > 3:1 | CRITICAL |
| **High Retransmissions** | >5% packet retransmit rate | MEDIUM |
| **Connection Timeouts** | Many failed handshakes | MEDIUM |
| **Unusual Ports** | High-numbered ports (>10000) | LOW-MEDIUM |
| **Data Exfiltration** | Large outbound to external IPs | HIGH |
| **C2 Beaconing** | Regular periodic connections | HIGH |

---

## 📊 Data to Extract from Logs

### KEEP:
- ✅ Timestamp
- ✅ Source IP & Port
- ✅ Destination IP & Port
- ✅ Protocol (TCP/UDP/ICMP)
- ✅ Packet size
- ✅ TCP Flags (SYN, ACK, RST, FIN, PSH, URG)
- ✅ Sequence numbers
- ✅ Window size
- ✅ TTL
- ✅ Retransmission indicators

### REMOVE:
- ❌ Full packet payloads
- ❌ Hex dumps
- ❌ Application layer data
- ❌ Duplicate entries
- ❌ Verbose debug info

---

## 🤖 LLM Prompt Template

```python
SYSTEM_PROMPT = """You are a network security analyst expert specializing in TCP/IP traffic analysis.

Analyze logs and identify:
1. Security threats (port scans, DDoS, suspicious connections)
2. Performance issues (latency, packet loss, retransmissions)
3. Configuration problems (routing, firewall misconfigs)

For each anomaly:
- Assign severity: CRITICAL, HIGH, MEDIUM, LOW
- Explain in plain English
- Describe WHY it's concerning
- Provide specific examples
- Suggest remediation steps"""

USER_PROMPT = """Analyze this network traffic:

SUMMARY:
- Total Packets: {count}
- Time Range: {start} to {end}
- Unique Source IPs: {sources}

BASELINE:
- Avg packet size: {avg_size}
- Normal connection rate: {rate}

SUSPICIOUS ACTIVITY:
{flagged_data}

Return JSON array of findings with format:
{
  "severity": "CRITICAL",
  "type": "port_scan",
  "title": "Port Scan Detected",
  "description": "Plain English explanation...",
  "evidence": {"source_ip": "...", "ports_scanned": 123},
  "why_it_matters": "Security impact...",
  "recommended_actions": ["Block IP", "Review firewall"]
}
"""
```

---

## 🎨 UI Color Scheme

```scss
$critical: #dc2626;  // Red
$high: #ea580c;      // Orange
$medium: #ca8a04;    // Yellow
$low: #2563eb;       // Blue
$info: #6b7280;      // Gray
$success: #16a34a;   // Green
```

---

## 📝 API Endpoints

### POST `/api/upload`
```json
// Request: multipart/form-data with file
// Response:
{
  "filename": "logs.txt",
  "size_mb": 45.2,
  "estimated_time": "2-3 minutes",
  "status": "uploaded"
}
```

### WebSocket `/ws/analyze`
```json
// Progress updates:
{
  "status": "parsing|analyzing|llm_analysis|complete|error",
  "progress": 60,
  "message": "Processing...",
  "results": {...}  // Only on complete
}
```

### GET `/health`
```json
{"status": "healthy"}
```

---

## 🧪 Testing Strategy

### 1. Generate Test Logs
```python
# Port scan test
generate_port_scan_pcapng(target_ports=150)
# Expected: Detect scan of 150 ports

# SYN flood test
generate_syn_flood_pcapng(syn_count=500)
# Expected: Detect high SYN/ACK ratio

# Normal traffic test
generate_normal_traffic_pcapng(connections=100)
# Expected: No anomalies detected
```

### 2. Validation Checks
- ✅ Parser handles PCAPNG and PCAP formats
- ✅ Detects all 6 anomaly types accurately
- ✅ LLM provides actionable recommendations
- ✅ UI warns for large files
- ✅ Progress updates work in real-time
- ✅ Export report works (JSON)

---

## 🚀 Performance Targets

| File Size | Expected Time | Implementation |
|-----------|---------------|----------------|
| <10MB | 30s - 1min | Full analysis |
| 10-50MB | 1-2 minutes | Chunk by time windows |
| 50-200MB | 2-5 minutes | Pre-filter outliers only |
| >200MB | 5-15 minutes | Heavy pre-filtering |

**Optimization Strategy:**
1. Statistical pre-filtering (70-80% reduction)
2. Only send suspicious traffic to LLM
3. Async processing with progress updates
4. Stream file reading (no full memory load)

---

## 🛡️ Security & Privacy

### Privacy-First Design:
- ✅ All processing happens locally
- ✅ No external API calls
- ✅ User controls all data
- ✅ LLM runs on user's machine
- ✅ Sensitive data not logged
- ✅ Memory cleared after analysis

### Data Handling Rules:
- ❌ Never log packet payloads
- ❌ Never send data to external servers
- ❌ Never store sensitive info
- ✅ Provide delete uploaded files option
- ✅ Export reports sanitized

---

## 📋 Implementation Checklist

### Phase 1: Setup (Week 1)
- [x] Install Ollama + Gemma 2 12B
- [x] Create Angular project
- [x] Create FastAPI backend
- [x] Test Ollama connection
- [x] Set up WebSocket

### Phase 2: Parsing (Week 2)
- [x] Implement PCAPNG parser using Scapy
- [x] Extract TCP/UDP/ICMP packet data
- [x] Build baseline calculator
- [x] Create statistical filters

### Phase 3: LLM Integration (Week 3)
- [x] Connect to Ollama
- [x] Engineer prompts
- [x] Implement chunking
- [x] Parse LLM responses
- [x] Test accuracy

### Phase 4: Frontend (Week 4)
- [ ] Build upload component
- [ ] Add drag-drop
- [ ] Create progress bar
- [ ] Design results display
- [ ] Add export function

### Phase 5: Testing (Week 5)
- [ ] Test all log formats
- [ ] Test all anomaly types
- [ ] Test large files (100MB+)
- [ ] Validate LLM accuracy
- [ ] Fix bugs

### Phase 6: Polish (Week 6)
- [ ] Refine UI/UX
- [ ] Add animations
- [ ] Write documentation
- [ ] Create user guide
- [ ] Final presentation prep

---

## 🎓 Key Success Metrics

1. **Accuracy**: >90% detection rate on test cases
2. **Speed**: <3 minutes for 50MB files
3. **Clarity**: Plain-English explanations
4. **Privacy**: Zero external calls
5. **Usability**: One-click upload & analyze
6. **Professionalism**: Stakeholder-ready quality

---

## 💡 Pro Tips

1. **Start with test data** - Generate known anomalies first
2. **Iterate on prompts** - Test LLM responses extensively
3. **Pre-filter aggressively** - Send only suspicious traffic to LLM
4. **Use WebSocket** - Real-time progress builds trust
5. **Color-code severity** - Visual hierarchy aids understanding
6. **Validate formats** - Handle malformed logs gracefully
7. **Profile performance** - Optimize bottlenecks early

---

## 📞 Common Issues & Solutions

### Issue: Ollama not responding
```bash
# Check Ollama is running
ollama list
# Restart if needed
ollama serve
```

### Issue: CORS errors
```python
# Verify CORS middleware in main.py
allow_origins=["http://localhost:4200"]
```

### Issue: Large file timeout
```python
# Increase timeout in uvicorn
uvicorn main:app --timeout-keep-alive=300
```

### Issue: LLM hallucinating
```
# Be more specific in prompts
# Add examples of correct output
# Validate JSON structure strictly
```

---

## 🎯 Final Deliverables

1. **Working Application**
   - Angular frontend on :4200
   - FastAPI backend on :8000
   - Gemma 2 12B integration
   - PCAPNG file support

2. **Documentation**
   - README with setup instructions
   - API documentation
   - User guide with screenshots
   - Architecture diagram

3. **Test Suite**
   - Sample PCAPNG files
   - Unit tests for parsers
   - Integration tests
   - Performance benchmarks

4. **Presentation Materials**
   - Demo script
   - Key screenshots
   - Metrics dashboard
   - Security/privacy highlights

---

## ✅ Definition of Done

Project is complete when:
- ✅ All 6 anomaly types detected correctly
- ✅ UI is professional and intuitive
- ✅ Large file handling works smoothly
- ✅ Documentation is comprehensive
- ✅ Privacy guarantees maintained
- ✅ Stakeholder demo-ready
- ✅ Code is clean and commented
- ✅ Tests pass (>90% coverage)

---

**Now go build something amazing!** 🚀

Remember: This is for your defense contractor internship. Quality matters. Take your time. Test thoroughly. Make it professional.

You've got this! 💪
