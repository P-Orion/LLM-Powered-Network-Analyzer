# Technical Specifications & Code Examples
## Supplementary Document for LLM Private Log Anomaly Finder

---

## 1. Sample Log Formats to Support

### Format 1: tcpdump Standard Output
```
14:25:32.123456 IP 192.168.1.100.52341 > 10.0.0.15.80: Flags [S], seq 1234567890, win 65535, length 0
14:25:32.125789 IP 10.0.0.15.80 > 192.168.1.100.52341: Flags [S.], seq 9876543210, ack 1234567891, win 29200, length 0
14:25:32.126123 IP 192.168.1.100.52341 > 10.0.0.15.80: Flags [.], ack 1, win 65535, length 0
```

### Format 2: Wireshark CSV Export
```csv
No.,Time,Source,Destination,Protocol,Length,Info
1,0.000000,192.168.1.100,10.0.0.15,TCP,74,52341 → 80 [SYN] Seq=0 Win=65535 Len=0
2,0.001333,10.0.0.15,192.168.1.100,TCP,74,80 → 52341 [SYN, ACK] Seq=0 Ack=1 Win=29200 Len=0
```

### Format 3: Cisco Router Logs
```
*Dec  2 14:25:32.123: %SEC-6-IPACCESSLOGP: list 101 permitted tcp 192.168.1.100(52341) -> 10.0.0.15(80), 1 packet
```

---

## 2. Backend API Structure

### File: `backend/main.py`
```python
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from typing import AsyncGenerator
import json

app = FastAPI(title="Log Anomaly Analyzer API")

# CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your modules
from parsers.log_parser import LogParser
from analyzers.anomaly_detector import AnomalyDetector
from llm.gemma_client import GemmaClient

@app.post("/api/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """Handle log file upload and return file info"""
    file_size = 0
    content = await file.read()
    file_size = len(content) / (1024 * 1024)  # MB
    
    return {
        "filename": file.filename,
        "size_mb": round(file_size, 2),
        "estimated_time": calculate_estimate(file_size),
        "status": "uploaded"
    }

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis updates"""
    await websocket.accept()
    
    try:
        # Receive file data
        data = await websocket.receive_json()
        file_content = data["content"]
        
        # Initialize components
        parser = LogParser()
        detector = AnomalyDetector()
        llm = GemmaClient()
        
        # Step 1: Parse logs
        await websocket.send_json({
            "status": "parsing",
            "progress": 20,
            "message": "Parsing log file..."
        })
        
        parsed_logs = await parser.parse(file_content)
        
        # Step 2: Statistical analysis
        await websocket.send_json({
            "status": "analyzing",
            "progress": 40,
            "message": "Calculating baselines..."
        })
        
        baseline = detector.calculate_baseline(parsed_logs)
        suspicious_entries = detector.flag_outliers(parsed_logs, baseline)
        
        # Step 3: LLM analysis
        await websocket.send_json({
            "status": "llm_analysis",
            "progress": 60,
            "message": "Analyzing anomalies with LLM..."
        })
        
        anomalies = await llm.analyze_anomalies(
            suspicious_entries, 
            baseline
        )
        
        # Step 4: Send results
        await websocket.send_json({
            "status": "complete",
            "progress": 100,
            "message": "Analysis complete",
            "results": anomalies
        })
        
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })
    
    await websocket.close()

def calculate_estimate(size_mb: float) -> str:
    """Calculate estimated processing time"""
    if size_mb < 10:
        return "30 seconds - 1 minute"
    elif size_mb < 50:
        return "1-2 minutes"
    elif size_mb < 100:
        return "2-4 minutes"
    else:
        return "5-15 minutes"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 3. Log Parser Implementation

### File: `backend/parsers/log_parser.py`
```python
import re
from datetime import datetime
from typing import List, Dict, Optional
import ipaddress

class LogParser:
    def __init__(self):
        self.patterns = {
            'tcpdump': re.compile(
                r'(\d{2}:\d{2}:\d{2}\.\d{6})\s+IP\s+'
                r'([\d\.]+)\.(\d+)\s+>\s+'
                r'([\d\.]+)\.(\d+):\s+'
                r'Flags\s+\[([^\]]+)\]'
            ),
            'wireshark_csv': None,  # CSV library handles this
            'cisco': re.compile(
                r'\*(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}\.\d{3}).*?'
                r'([\d\.]+)\((\d+)\)\s+->\s+'
                r'([\d\.]+)\((\d+)\)'
            )
        }
    
    async def parse(self, content: str) -> List[Dict]:
        """Main parsing function - detects format and parses"""
        lines = content.split('\n')
        format_type = self.detect_format(lines)
        
        if format_type == 'tcpdump':
            return self.parse_tcpdump(lines)
        elif format_type == 'csv':
            return self.parse_csv(content)
        elif format_type == 'cisco':
            return self.parse_cisco(lines)
        else:
            raise ValueError("Unknown log format")
    
    def detect_format(self, lines: List[str]) -> str:
        """Detect log format from first few lines"""
        sample = '\n'.join(lines[:10])
        
        if 'IP' in sample and 'Flags' in sample:
            return 'tcpdump'
        elif 'No.,Time,Source' in sample:
            return 'csv'
        elif '%SEC-' in sample or 'list' in sample:
            return 'cisco'
        return 'unknown'
    
    def parse_tcpdump(self, lines: List[str]) -> List[Dict]:
        """Parse tcpdump format logs"""
        parsed = []
        
        for line in lines:
            match = self.patterns['tcpdump'].search(line)
            if match:
                timestamp, src_ip, src_port, dst_ip, dst_port, flags = match.groups()
                
                parsed.append({
                    'timestamp': timestamp,
                    'source_ip': src_ip,
                    'source_port': int(src_port),
                    'dest_ip': dst_ip,
                    'dest_port': int(dst_port),
                    'tcp_flags': flags.replace('.', '').replace(' ', ''),
                    'protocol': 'TCP',
                    'raw_line': line
                })
        
        return parsed
    
    def parse_csv(self, content: str) -> List[Dict]:
        """Parse Wireshark CSV format"""
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(content))
        parsed = []
        
        for row in reader:
            # Extract port from Info field if available
            info = row.get('Info', '')
            port_match = re.search(r'(\d+)\s*→\s*(\d+)', info)
            
            if port_match:
                src_port, dst_port = port_match.groups()
                parsed.append({
                    'timestamp': row.get('Time', '0'),
                    'source_ip': row.get('Source', ''),
                    'source_port': int(src_port),
                    'dest_ip': row.get('Destination', ''),
                    'dest_port': int(dst_port),
                    'protocol': row.get('Protocol', ''),
                    'length': int(row.get('Length', 0)),
                    'tcp_flags': self.extract_flags(info),
                    'info': info
                })
        
        return parsed
    
    def extract_flags(self, info: str) -> str:
        """Extract TCP flags from info string"""
        flags = ''
        if '[SYN]' in info: flags += 'S'
        if '[ACK]' in info: flags += 'A'
        if '[FIN]' in info: flags += 'F'
        if '[RST]' in info: flags += 'R'
        if '[PSH]' in info: flags += 'P'
        return flags
```

---

## 4. Anomaly Detection Logic

### File: `backend/analyzers/anomaly_detector.py`
```python
from collections import defaultdict, Counter
from typing import List, Dict
import statistics

class AnomalyDetector:
    def __init__(self):
        self.thresholds = {
            'port_scan_count': 20,  # Connections to > 20 ports
            'port_scan_time': 60,   # Within 60 seconds
            'syn_flood_ratio': 3.0, # SYN/ACK ratio > 3
            'retransmit_threshold': 0.05,  # 5% retransmission rate
            'connection_rate': 100  # > 100 connections per second
        }
    
    def calculate_baseline(self, logs: List[Dict]) -> Dict:
        """Calculate normal traffic patterns"""
        if not logs:
            return {}
        
        packet_sizes = [log.get('length', 0) for log in logs if log.get('length')]
        
        # Connection statistics
        connections = defaultdict(set)
        for log in logs:
            src = log.get('source_ip')
            dst = log.get('dest_ip')
            dst_port = log.get('dest_port')
            if src and dst and dst_port:
                connections[src].add((dst, dst_port))
        
        return {
            'avg_packet_size': statistics.mean(packet_sizes) if packet_sizes else 0,
            'median_packet_size': statistics.median(packet_sizes) if packet_sizes else 0,
            'total_packets': len(logs),
            'unique_sources': len(set(log.get('source_ip') for log in logs)),
            'unique_destinations': len(set(log.get('dest_ip') for log in logs)),
            'avg_connections_per_host': sum(len(v) for v in connections.values()) / len(connections) if connections else 0,
            'protocol_distribution': Counter(log.get('protocol') for log in logs)
        }
    
    def flag_outliers(self, logs: List[Dict], baseline: Dict) -> List[Dict]:
        """Flag suspicious entries based on statistical analysis"""
        suspicious = []
        
        # Check for port scans
        port_scans = self.detect_port_scans(logs)
        suspicious.extend(port_scans)
        
        # Check for SYN floods
        syn_floods = self.detect_syn_floods(logs)
        suspicious.extend(syn_floods)
        
        # Check for high retransmission rates
        retransmits = self.detect_retransmissions(logs)
        suspicious.extend(retransmits)
        
        # Check for connection anomalies
        conn_anomalies = self.detect_connection_anomalies(logs, baseline)
        suspicious.extend(conn_anomalies)
        
        return suspicious
    
    def detect_port_scans(self, logs: List[Dict]) -> List[Dict]:
        """Detect port scanning behavior"""
        scans = []
        port_attempts = defaultdict(lambda: defaultdict(set))
        
        for log in logs:
            src_ip = log.get('source_ip')
            dst_ip = log.get('dest_ip')
            dst_port = log.get('dest_port')
            timestamp = log.get('timestamp', '')
            
            if src_ip and dst_ip and dst_port:
                port_attempts[src_ip][dst_ip].add(dst_port)
        
        for src_ip, targets in port_attempts.items():
            for dst_ip, ports in targets.items():
                if len(ports) > self.thresholds['port_scan_count']:
                    scans.append({
                        'type': 'port_scan',
                        'severity': 'CRITICAL',
                        'source_ip': src_ip,
                        'target_ip': dst_ip,
                        'ports_scanned': len(ports),
                        'sample_ports': sorted(list(ports))[:10]
                    })
        
        return scans
    
    def detect_syn_floods(self, logs: List[Dict]) -> List[Dict]:
        """Detect SYN flood attacks"""
        floods = []
        flag_counts = defaultdict(lambda: {'SYN': 0, 'SYNACK': 0})
        
        for log in logs:
            src_ip = log.get('source_ip')
            flags = log.get('tcp_flags', '')
            
            if 'S' in flags and 'A' not in flags:
                flag_counts[src_ip]['SYN'] += 1
            elif 'S' in flags and 'A' in flags:
                flag_counts[src_ip]['SYNACK'] += 1
        
        for src_ip, counts in flag_counts.items():
            if counts['SYNACK'] > 0:
                ratio = counts['SYN'] / counts['SYNACK']
                if ratio > self.thresholds['syn_flood_ratio']:
                    floods.append({
                        'type': 'syn_flood',
                        'severity': 'CRITICAL',
                        'source_ip': src_ip,
                        'syn_count': counts['SYN'],
                        'synack_count': counts['SYNACK'],
                        'ratio': round(ratio, 2)
                    })
        
        return floods
    
    def detect_retransmissions(self, logs: List[Dict]) -> List[Dict]:
        """Detect high retransmission rates"""
        # This requires sequence number tracking
        # Simplified version here
        return []
    
    def detect_connection_anomalies(self, logs: List[Dict], baseline: Dict) -> List[Dict]:
        """Detect unusual connection patterns"""
        anomalies = []
        
        # Check for connections to unusual ports
        common_ports = {21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995}
        unusual_connections = []
        
        for log in logs:
            dst_port = log.get('dest_port')
            if dst_port and dst_port > 10000 and dst_port not in common_ports:
                unusual_connections.append(log)
        
        if len(unusual_connections) > 100:
            anomalies.append({
                'type': 'unusual_ports',
                'severity': 'MEDIUM',
                'count': len(unusual_connections),
                'description': f'Detected {len(unusual_connections)} connections to high-numbered ports'
            })
        
        return anomalies
```

---

## 5. LLM Client Implementation

### File: `backend/llm/gemma_client.py`
```python
import ollama
from typing import List, Dict
import json

class GemmaClient:
    def __init__(self):
        self.model = "gemma:12b"
        self.system_prompt = """You are a network security analyst expert specializing in TCP/IP traffic analysis and anomaly detection. 
        
Analyze network log data and identify security threats, performance issues, and anomalies.

For each anomaly detected:
- Assign severity: CRITICAL, HIGH, MEDIUM, LOW
- Explain what you found in plain English
- Describe WHY it's concerning
- Provide specific packet/connection examples
- Suggest concrete remediation steps

Be precise but accessible."""
    
    async def analyze_anomalies(self, suspicious_data: List[Dict], baseline: Dict) -> Dict:
        """Send data to LLM for analysis"""
        
        # Prepare prompt
        prompt = self.build_analysis_prompt(suspicious_data, baseline)
        
        # Call Ollama
        response = ollama.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': prompt}
            ]
        )
        
        # Parse response
        analysis = self.parse_llm_response(response['message']['content'])
        
        return analysis
    
    def build_analysis_prompt(self, suspicious_data: List[Dict], baseline: Dict) -> str:
        """Build comprehensive analysis prompt"""
        prompt = f"""Analyze the following network traffic data for anomalies:

TRAFFIC SUMMARY:
- Total Packets: {baseline.get('total_packets', 0)}
- Unique Source IPs: {baseline.get('unique_sources', 0)}
- Unique Destination IPs: {baseline.get('unique_destinations', 0)}
- Average Packet Size: {baseline.get('avg_packet_size', 0):.2f} bytes

STATISTICAL BASELINE:
- Average connections per host: {baseline.get('avg_connections_per_host', 0):.2f}
- Protocol distribution: {dict(baseline.get('protocol_distribution', {}))}

FLAGGED SUSPICIOUS ACTIVITY:
"""
        
        for item in suspicious_data[:20]:  # Limit to top 20
            prompt += f"\n{json.dumps(item, indent=2)}\n"
        
        prompt += """

Identify and report security threats, performance issues, and unusual patterns.

For each finding, provide in JSON format:
{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "type": "descriptive_type",
  "title": "Short title",
  "description": "Plain English explanation",
  "evidence": {"key": "value"},
  "why_it_matters": "Security/performance impact",
  "recommended_actions": ["action1", "action2"]
}

Return as a JSON array of findings."""
        
        return prompt
    
    def parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                anomalies = json.loads(json_str)
                
                # Count by severity
                summary = {
                    'critical': sum(1 for a in anomalies if a.get('severity') == 'CRITICAL'),
                    'high': sum(1 for a in anomalies if a.get('severity') == 'HIGH'),
                    'medium': sum(1 for a in anomalies if a.get('severity') == 'MEDIUM'),
                    'low': sum(1 for a in anomalies if a.get('severity') == 'LOW')
                }
                
                return {
                    'summary': summary,
                    'total_anomalies': len(anomalies),
                    'anomalies': anomalies
                }
            else:
                # Fallback: return raw response
                return {
                    'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                    'total_anomalies': 0,
                    'anomalies': [],
                    'raw_response': response
                }
        except Exception as e:
            return {
                'error': str(e),
                'raw_response': response
            }
```

---

## 6. Angular Service for WebSocket Communication

### File: `frontend/src/app/services/analysis.service.ts`
```typescript
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface AnalysisProgress {
  status: string;
  progress: number;
  message: string;
  results?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {
  private ws: WebSocket | null = null;
  private progressSubject = new Subject<AnalysisProgress>();

  analyzeFile(fileContent: string): Observable<AnalysisProgress> {
    this.ws = new WebSocket('ws://localhost:8000/ws/analyze');
    
    this.ws.onopen = () => {
      this.ws?.send(JSON.stringify({
        content: fileContent
      }));
    };
    
    this.ws.onmessage = (event) => {
      const data: AnalysisProgress = JSON.parse(event.data);
      this.progressSubject.next(data);
      
      if (data.status === 'complete' || data.status === 'error') {
        this.ws?.close();
      }
    };
    
    this.ws.onerror = (error) => {
      this.progressSubject.next({
        status: 'error',
        progress: 0,
        message: 'Connection error'
      });
    };
    
    return this.progressSubject.asObservable();
  }
}
```

---

## 7. Sample Test Data Generator

### File: `backend/tests/generate_test_logs.py`
```python
import random
from datetime import datetime, timedelta

def generate_port_scan_log(count=100):
    """Generate log with port scanning behavior"""
    scanner_ip = "192.168.1.45"
    target_ip = "10.0.0.15"
    start_time = datetime.now()
    
    logs = []
    for i in range(count):
        timestamp = start_time + timedelta(seconds=i*0.1)
        port = 20 + i
        
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {scanner_ip}.{50000+i} > "
            f"{target_ip}.{port}: Flags [S], seq {random.randint(1000000, 9999999)}, win 65535, length 0"
        )
    
    return '\n'.join(logs)

def generate_syn_flood_log(count=500):
    """Generate log with SYN flood behavior"""
    attacker_ip = "203.0.113.42"
    target_ip = "10.0.0.20"
    start_time = datetime.now()
    
    logs = []
    for i in range(count):
        timestamp = start_time + timedelta(milliseconds=i*5)
        
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {attacker_ip}.{random.randint(40000, 60000)} > "
            f"{target_ip}.80: Flags [S], seq {random.randint(1000000, 9999999)}, win 65535, length 0"
        )
    
    return '\n'.join(logs)

def generate_clean_log(count=200):
    """Generate clean normal traffic"""
    ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
    servers = ["10.0.0.5", "10.0.0.6"]
    ports = [80, 443, 22]
    
    start_time = datetime.now()
    logs = []
    
    for i in range(count):
        timestamp = start_time + timedelta(seconds=i*0.5)
        src_ip = random.choice(ips)
        dst_ip = random.choice(servers)
        port = random.choice(ports)
        
        # Complete handshake
        logs.append(f"{timestamp.strftime('%H:%M:%S.%f')} IP {src_ip}.{50000+i} > {dst_ip}.{port}: Flags [S], seq {random.randint(1000000, 9999999)}, win 65535, length 0")
        logs.append(f"{(timestamp + timedelta(milliseconds=2)).strftime('%H:%M:%S.%f')} IP {dst_ip}.{port} > {src_ip}.{50000+i}: Flags [S.], seq {random.randint(1000000, 9999999)}, ack 1, win 29200, length 0")
        logs.append(f"{(timestamp + timedelta(milliseconds=3)).strftime('%H:%M:%S.%f')} IP {src_ip}.{50000+i} > {dst_ip}.{port}: Flags [.], ack 1, win 65535, length 0")
    
    return '\n'.join(logs)

if __name__ == "__main__":
    # Generate test files
    with open('test_port_scan.log', 'w') as f:
        f.write(generate_port_scan_log(150))
    
    with open('test_syn_flood.log', 'w') as f:
        f.write(generate_syn_flood_log(500))
    
    with open('test_clean.log', 'w') as f:
        f.write(generate_clean_log(200))
    
    print("Test log files generated!")
```

---

## Quick Start Checklist

1. **Environment Setup:**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull gemma:12b
   
   # Backend
   python -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn ollama websockets python-multipart
   
   # Frontend
   npm install -g @angular/cli
   ng new log-analyzer
   cd log-analyzer && npm install
   ```

2. **Test Ollama is Working:**
   ```python
   import ollama
   response = ollama.chat(model='gemma:12b', messages=[
     {'role': 'user', 'content': 'Hello!'}
   ])
   print(response)
   ```

3. **Generate Test Data:**
   ```bash
   python backend/tests/generate_test_logs.py
   ```

4. **Run Application:**
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend && ng serve --port 4200
   ```

5. **Test with Sample Log:**
   - Open http://localhost:4200
   - Upload test_port_scan.log
   - Verify detection works

---

This document provides all the technical implementation details needed to build the system! 🚀
