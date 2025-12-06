# Build: LLM Private Log Anomaly Finder - Complete Implementation

## Project Overview
Build a **standalone, privacy-focused network log anomaly detection tool** that runs entirely locally on localhost:4200. This application allows users to upload TCP network logs, automatically parse and analyze them using a local LLM (Gemma 12B), and receive plain-English reports about detected anomalies with actionable solutions.

---

## Technical Stack Requirements

### Frontend
- **Framework**: Angular (for localhost:4200 compatibility)
- **UI Library**: Angular Material or Tailwind CSS for modern, clean design
- **File Upload**: Support drag-and-drop and file picker
- **Real-time Updates**: Display analysis progress and streaming results

### Backend
- **Framework**: Python FastAPI or Node.js Express
- **LLM Integration**: Ollama running Gemma 12B locally
- **Log Parsing**: Custom parser with regex/pattern matching
- **Processing**: Async processing for large files

### Local LLM Setup
- **Model**: Gemma 12B via Ollama
- **Inference**: Local inference with no external API calls
- **Context Window**: Optimize chunking for large log files

---

## Core Features & Implementation Details

### 1. Log File Upload & Validation
**Requirements:**
- Accept common log formats: .log, .txt, .pcap (convert to text), .csv
- Drag-and-drop interface with file size display
- Validate file type and warn if file > 50MB that processing may take 2-5 minutes
- Show upload progress indicator

**Implementation Notes:**
```
- Maximum file size: 500MB (warn at 50MB+)
- Supported formats: TCP logs, Wireshark exports, router/switch logs
- Pre-upload validation: file type, size, basic format check
```

### 2. TCP Log Parsing & Data Extraction

**CRITICAL: Research and implement proper TCP log analysis**

You MUST research and implement detection for these common TCP network anomalies:

#### Network Anomalies to Detect:
1. **Port Scanning Activities**
   - Multiple connection attempts to sequential ports
   - High volume of SYN packets without ACK responses
   - Connections to unusual high-numbered ports

2. **DDoS/Flooding Attacks**
   - Unusually high packet rate from single source
   - SYN flood: many SYN packets without completing handshake
   - UDP flood: high volume of UDP packets
   - Traffic volume spikes (baseline deviation)

3. **Connection Issues**
   - High number of TCP retransmissions
   - Connection timeouts and failed handshakes
   - Excessive RST (reset) packets
   - Window size anomalies

4. **Latency Problems**
   - High round-trip times (RTT)
   - Packet loss indicators
   - Out-of-order packet delivery
   - Delayed ACK patterns

5. **Suspicious Traffic Patterns**
   - Data exfiltration: large outbound transfers to external IPs
   - Beaconing: regular periodic connections (C2 communication)
   - Protocol violations: malformed packets
   - Unusual protocol usage on non-standard ports

6. **Authentication/Security Issues**
   - Failed connection attempts patterns
   - Access to blocked/unauthorized ports
   - Geographic anomalies (unexpected source locations if logged)

#### Data to KEEP:
```
- Timestamp (critical for pattern detection)
- Source IP and Port
- Destination IP and Port  
- Protocol (TCP/UDP/ICMP)
- Packet size/length
- TCP Flags (SYN, ACK, RST, FIN, PSH, URG)
- Sequence/Acknowledgment numbers
- Window size
- TTL (Time to Live)
- Retransmission indicators
- Connection state
- Latency/RTT if available
```

#### Data to REMOVE:
```
- Full packet payloads (privacy)
- Detailed hex dumps
- Application layer data (unless showing protocol violations)
- Redundant duplicate entries
- Non-essential header fields
- System-specific verbose debug info
```

**Parsing Strategy:**
```python
# Pseudocode structure
1. Identify log format (tcpdump, Wireshark, router logs, etc.)
2. Extract relevant fields using regex/parsing library
3. Convert to normalized JSON structure
4. Aggregate statistics (connections per IP, port usage, timing patterns)
5. Calculate baseline metrics (normal traffic volume, typical packet sizes)
6. Flag statistical outliers
7. Chunk large datasets for LLM processing (max 4000 tokens per chunk)
```

### 3. Local LLM Integration with Prompt Engineering

**LLM Setup:**
```bash
# Ensure Ollama is installed and Gemma 12B is pulled
ollama pull gemma:12b
```

**Prompt Engineering - System Prompt:**
```
You are a network security analyst expert specializing in TCP/IP traffic analysis and anomaly detection. Your role is to analyze parsed network log data and identify potential security threats, performance issues, and anomalies.

When analyzing logs, focus on:
1. Security threats (port scans, DDoS, suspicious connections)
2. Performance issues (high latency, packet loss, retransmissions)
3. Configuration problems (routing issues, firewall misconfigurations)
4. Unusual patterns (data exfiltration, C2 beaconing, protocol violations)

For each anomaly detected:
- Assign severity: CRITICAL, HIGH, MEDIUM, LOW
- Explain what you found in plain English
- Describe WHY it's concerning
- Provide specific packet/connection examples
- Suggest concrete remediation steps

Be precise but accessible - assume the user understands networking basics but needs clear guidance.
```

**Analysis Prompt Template:**
```
Analyze the following network traffic data for anomalies:

TRAFFIC SUMMARY:
- Time Range: [start] to [end]
- Total Packets: [count]
- Unique Source IPs: [count]
- Unique Destination IPs: [count]
- Top Protocols: [list]

STATISTICAL BASELINES:
- Average packet size: [value]
- Normal connection rate: [value]
- Typical port distribution: [value]

PARSED LOG DATA:
[Insert normalized, chunked log data here]

Identify and report:
1. Any security threats or suspicious activities
2. Performance or connectivity issues
3. Configuration problems
4. Unusual traffic patterns

For each finding, provide:
- Severity level
- Clear description in plain English
- Specific evidence (IPs, ports, timestamps)
- Why it matters
- Recommended actions to resolve
```

**Chunking Strategy for Large Files:**
```
- If log has < 1000 entries: analyze in single pass
- If log has 1000-10000 entries: chunk by time windows (e.g., 5-minute intervals)
- If log has > 10000 entries: 
  1. Pre-filter to statistical outliers
  2. Analyze suspicious traffic in detail
  3. Provide summary statistics for normal traffic
```

### 4. User Interface Design

**Layout Structure:**

```
┌─────────────────────────────────────────────────────┐
│  🔍 LLM Private Log Anomaly Finder                  │
│  Secure Local Analysis • No Data Leaves Your Device │
├─────────────────────────────────────────────────────┤
│                                                     │
│   ┌───────────────────────────────────────┐       │
│   │  📁 Drag & Drop Log File Here         │       │
│   │     or click to browse                │       │
│   │                                        │       │
│   │  Supported: .log, .txt, .pcap, .csv   │       │
│   └───────────────────────────────────────┘       │
│                                                     │
│   [Analysis Status]                                │
│   ⚠️  Large file detected (125MB)                  │
│   Estimated analysis time: 3-4 minutes             │
│                                                     │
│   Progress: ████████░░ 80% Analyzing packets...    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ANALYSIS RESULTS                                   │
│                                                     │
│  🔴 CRITICAL (2 found)                              │
│  ├─ Possible Port Scan Detected                    │
│  │  IP: 192.168.1.45 scanned 1,247 ports           │
│  │  Details: Sequential port scanning from...      │
│  │  ✓ Solution: Block source IP, review firewall   │
│  │                                                  │
│  │  [View Packets] [Export Details]                │
│  └─────────────────────────────────────────────────┤
│                                                     │
│  🟡 MEDIUM (5 found)                                │
│  ├─ High Retransmission Rate                       │
│  │  Between: 10.0.0.5 ↔ 10.0.0.20                  │
│  │  Details: 15% packet retransmission rate...     │
│  │  ✓ Solution: Check network cable, switch port   │
│  │                                                  │
│  │  [View Packets] [Export Details]                │
│                                                     │
│  [Download Full Report] [Analyze Another File]     │
└─────────────────────────────────────────────────────┘
```

**UI Components:**
1. **Header**: App title, privacy badge
2. **Upload Zone**: Large, prominent drag-drop area
3. **Status Panel**: File info, processing time estimate
4. **Progress Indicator**: Real-time analysis progress
5. **Results Panel**: 
   - Severity-coded sections (color-coded)
   - Collapsible anomaly cards
   - Plain-English descriptions
   - Actionable recommendations
   - Packet detail views
6. **Export Options**: Download PDF/JSON report

**Color Scheme:**
- Critical: Red (#dc2626)
- High: Orange (#ea580c)  
- Medium: Yellow (#ca8a04)
- Low: Blue (#2563eb)
- Info: Gray (#6b7280)
- Success: Green (#16a34a)

### 5. Performance Optimization

**File Size Handling:**
```javascript
// Frontend warning logic
if (fileSize > 50MB && fileSize <= 200MB) {
  showWarning("Large file detected. Analysis may take 2-5 minutes.");
} else if (fileSize > 200MB) {
  showWarning("Very large file detected. Analysis may take 5-15 minutes. Consider filtering logs before upload.");
}
```

**Backend Processing:**
- Stream file reading (don't load entire file into memory)
- Process in chunks asynchronously
- Send progress updates via WebSocket or SSE
- Implement timeout protection (max 30 minutes)
- Cache parsed results for re-analysis

### 6. Output Format & Reporting

**JSON Structure for Results:**
```json
{
  "analysis_timestamp": "2025-10-06T14:30:00Z",
  "file_info": {
    "name": "network_logs.txt",
    "size_mb": 125.4,
    "packet_count": 15847,
    "time_range": {
      "start": "2025-10-06T10:00:00Z",
      "end": "2025-10-06T12:00:00Z"
    }
  },
  "summary": {
    "total_anomalies": 7,
    "critical": 2,
    "high": 0,
    "medium": 5,
    "low": 0
  },
  "anomalies": [
    {
      "severity": "CRITICAL",
      "type": "port_scan",
      "title": "Possible Port Scan Detected",
      "description": "Host 192.168.1.45 attempted connections to 1,247 sequential ports on target 10.0.0.15 within a 3-minute window. This pattern is characteristic of automated port scanning tools.",
      "evidence": {
        "source_ip": "192.168.1.45",
        "target_ip": "10.0.0.15",
        "ports_scanned": 1247,
        "time_window": "180 seconds",
        "sample_packets": ["12:05:32.123 SYN 192.168.1.45:54321 -> 10.0.0.15:80", "..."]
      },
      "why_it_matters": "Port scanning is often reconnaissance before an attack. The scanning host may be compromised or an attacker is mapping your network for vulnerabilities.",
      "recommended_actions": [
        "Immediately block 192.168.1.45 at the firewall",
        "Check if 192.168.1.45 is an authorized device on your network",
        "Review firewall rules to rate-limit connection attempts",
        "Scan 192.168.1.45 for malware if it's an internal device",
        "Monitor 10.0.0.15 for any successful unauthorized access"
      ]
    }
  ]
}
```

---

## Implementation Steps

### Phase 1: Setup & Architecture (Do This First)
1. Set up Angular project with `ng new log-analyzer --routing`
2. Set up Python FastAPI backend
3. Install and configure Ollama with Gemma 12B
4. Create project structure:
   ```
   /frontend (Angular)
   /backend (FastAPI)
   /models (LLM configs)
   /parsers (Log parsing logic)
   /prompts (LLM prompt templates)
   ```

### Phase 2: Core Parsing Logic
1. Research TCP log formats (tcpdump, Wireshark, common router formats)
2. Implement log parser with regex patterns
3. Create data extraction and normalization functions
4. Build statistical baseline calculator
5. Implement anomaly detection rules (pre-LLM filtering)

### Phase 3: LLM Integration
1. Set up Ollama API connection
2. Create prompt templates with examples
3. Implement chunking strategy for large logs
4. Build LLM response parser
5. Test prompt effectiveness with sample logs

### Phase 4: Frontend Development
1. Build upload component with drag-drop
2. Create file validation and warning logic
3. Implement progress tracking (WebSocket/SSE)
4. Design results display with severity levels
5. Add export functionality (PDF/JSON)

### Phase 5: Integration & Testing
1. Connect frontend to backend API
2. Test with various log formats and sizes
3. Validate anomaly detection accuracy
4. Optimize performance for large files
5. Error handling and edge cases

### Phase 6: Polish & Documentation
1. Refine UI/UX based on testing
2. Add loading animations and transitions
3. Create user documentation
4. Package as standalone application (optional: Electron wrapper)

---

## Key Technical Decisions

**Why localhost:4200?**
- Standard Angular dev server port
- Easy for local development and testing
- User keeps complete control over data

**Why Gemma 12B?**
- Runs efficiently on consumer hardware
- Good balance of performance and accuracy
- Local inference ensures privacy

**Why FastAPI?**
- Modern async Python framework
- Easy WebSocket support for progress updates
- Clean API documentation
- Fast development

**Chunking Strategy:**
- Pre-filter logs using statistical methods
- Only send anomalous/suspicious traffic to LLM
- Reduces LLM inference time by 70-80%
- Maintains accuracy for security findings

---

## Testing Checklist

Create test cases for:
- ✅ Small log file (< 1MB)
- ✅ Medium log file (10-50MB)
- ✅ Large log file (100-200MB)
- ✅ Known port scan pattern
- ✅ Known DDoS pattern
- ✅ Connection timeout issues
- ✅ High retransmission scenario
- ✅ Clean traffic (no anomalies)
- ✅ Malformed log file (error handling)
- ✅ Multiple concurrent analyses

---

## Security & Privacy Notes

**Privacy-First Design:**
- All processing happens locally
- No data sent to external servers
- LLM runs on user's machine
- User controls all data retention

**Data Handling:**
- Don't log sensitive packet data
- Clear memory after analysis
- Provide option to delete uploaded files
- Export reports don't contain raw packet data unless user requests

---

## Deliverables

1. **Functional Application:**
   - Angular frontend (localhost:4200)
   - FastAPI backend with Ollama integration
   - Log parser with anomaly detection
   - Clean, intuitive UI

2. **Documentation:**
   - README with setup instructions
   - API documentation
   - User guide with examples
   - Sample log files for testing

3. **Code Quality:**
   - Clean, commented code
   - Error handling throughout
   - Type hints (Python)
   - Unit tests for parsing logic

---

## Getting Started Commands

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn ollama python-multipart aiofiles
ollama pull gemma:12b

# Frontend setup
cd frontend
npm install
ng serve

# Run application
# Terminal 1: uvicorn backend.main:app --reload --port 8000
# Terminal 2: ng serve --port 4200
# Open browser: http://localhost:4200
```

---

## Success Criteria

The project is complete when:
1. ✅ User can upload TCP logs via clean UI
2. ✅ Application parses logs and extracts relevant data
3. ✅ Statistical baselines are calculated automatically
4. ✅ LLM identifies anomalies with >90% accuracy on test cases
5. ✅ Results display in plain English with actionable steps
6. ✅ Large file processing shows progress and time estimates
7. ✅ Entire application runs locally without external dependencies
8. ✅ UI is professional and intuitive
9. ✅ Export functionality works for reports
10. ✅ Documentation is clear and complete

---

## FINAL NOTE TO CLAUDE CODE:

This is a **real internship project** for a Computer Science student working in defense contracting. The tool needs to be:
- **Professional quality** - this will be presented to stakeholders
- **Actually functional** - not just a demo
- **Privacy-focused** - critical for defense/security contexts
- **Well-documented** - others will need to understand it

Take your time to build this correctly. Research TCP log formats thoroughly. Test the LLM prompts extensively. Make the UI clean and professional.

You have all the information you need. Build something great! 🚀
