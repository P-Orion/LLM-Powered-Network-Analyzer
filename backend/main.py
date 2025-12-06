from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Optional

# Import our modules
from parsers.log_parser import LogParser
from analyzers.anomaly_detector import AnomalyDetector
from llm.gemma_client import GemmaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Log Anomaly Analyzer API",
    description="Privacy-focused TCP network log analysis using local LLM",
    version="1.0.0"
)

# CORS configuration for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        JSON with status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Log Anomaly Analyzer API"
    }


@app.post("/api/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """
    Handle log file upload and return file metadata.

    Args:
        file: Uploaded file

    Returns:
        JSON with file info and estimated processing time
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension - only allow pcapng files
        allowed_extensions = {'.pcapng', '.pcap'}
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if f'.{file_ext}' not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Only .pcapng and .pcap files are supported. Got: .{file_ext}"
            )
        
        # Read file content with size limit (500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        content = await file.read()
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(content) / (1024 * 1024):.1f}MB"
            )
        
        file_size_mb = len(content) / (1024 * 1024)

        # For pcapng files, we work with binary content, not text
        # Validate that it's a proper pcapng file
        parser = LogParser()
        if not parser.validate_pcapng_file(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid pcapng file format. Please upload a valid pcapng or pcap file."
            )

        # Get file statistics
        file_stats = parser.get_file_stats(content)
        if file_stats.get('total_packets', 0) == 0:
            raise HTTPException(
                status_code=400,
                detail="No packets found in the pcapng file or file is corrupted."
            )

        # Estimate processing time based on packet count
        packet_count = file_stats.get('total_packets', 0)
        estimated_time = calculate_estimate_by_packets(packet_count)

        # Detect format
        detected_format = parser.detect_format(content)
        
        logger.info(f"PCAPNG file uploaded: {file.filename}, Size: {file_size_mb:.2f}MB, Packets: {packet_count}, Format: {detected_format}")

        return {
            "filename": file.filename,
            "size_mb": round(file_size_mb, 2),
            "estimated_time": estimated_time,
            "packet_count": packet_count,
            "detected_format": detected_format,
            "protocols": file_stats.get('protocols', {}),
            "time_range": file_stats.get('time_range'),
            "status": "uploaded"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def format_statistical_anomalies(suspicious_entries: list) -> dict:
    """
    Format statistical anomalies into structured output when LLM is unavailable.

    Args:
        suspicious_entries: Raw suspicious entries from statistical analysis

    Returns:
        Dictionary matching LLM output format
    """
    anomalies = []
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    for entry in suspicious_entries:
        anomaly_type = entry.get('type', 'unknown')

        # Determine severity based on type
        if anomaly_type in ['port_scan', 'syn_flood']:
            severity = 'CRITICAL'
            severity_counts['critical'] += 1
        elif anomaly_type in ['retransmission', 'connection_anomaly']:
            severity = 'HIGH'
            severity_counts['high'] += 1
        elif anomaly_type == 'unusual_port':
            severity = 'MEDIUM'
            severity_counts['medium'] += 1
        else:
            severity = 'LOW'
            severity_counts['low'] += 1

        # Format anomaly with proper structure
        anomaly = {
            'severity': severity,
            'type': anomaly_type,
            'title': entry.get('description', f'{anomaly_type.replace("_", " ").title()} Detected'),
            'description': entry.get('details', entry.get('description', 'Suspicious activity detected')),
            'evidence': {
                'source': entry.get('src_ip', 'N/A'),
                'destination': entry.get('dst_ip', 'N/A'),
                'port': entry.get('port', entry.get('dst_port', 'N/A')),
                'count': entry.get('count', 1)
            },
            'why_it_matters': get_impact_description(anomaly_type),
            'recommended_actions': get_recommended_actions(anomaly_type)
        }
        anomalies.append(anomaly)

    return {
        'summary': severity_counts,
        'total_anomalies': len(anomalies),
        'anomalies': anomalies,
        'status': 'statistical_fallback',
        'note': 'Results from statistical analysis (LLM unavailable)'
    }


def get_impact_description(anomaly_type: str) -> str:
    """Get impact description for anomaly type."""
    impacts = {
        'port_scan': 'May indicate reconnaissance activity before an attack',
        'syn_flood': 'Could lead to service disruption or denial of service',
        'retransmission': 'May indicate network congestion or packet loss',
        'connection_anomaly': 'Could indicate connection issues or scanning activity',
        'unusual_port': 'May indicate unauthorized services or data exfiltration',
        'suspicious_pattern': 'Could indicate malicious activity or policy violation'
    }
    return impacts.get(anomaly_type, 'Unusual network behavior detected')


def get_recommended_actions(anomaly_type: str) -> list:
    """Get recommended actions for anomaly type."""
    actions = {
        'port_scan': [
            'Block source IP if unauthorized',
            'Review firewall rules',
            'Monitor for further scanning activity'
        ],
        'syn_flood': [
            'Enable SYN cookies on affected servers',
            'Implement rate limiting',
            'Consider blocking source IP'
        ],
        'retransmission': [
            'Check network infrastructure for issues',
            'Analyze bandwidth usage patterns',
            'Review server performance metrics'
        ],
        'connection_anomaly': [
            'Investigate failed connections',
            'Review server logs for errors',
            'Check firewall configuration'
        ],
        'unusual_port': [
            'Verify legitimate service on this port',
            'Review running processes on host',
            'Consider blocking if unauthorized'
        ],
        'suspicious_pattern': [
            'Investigate source and destination hosts',
            'Review related traffic patterns',
            'Monitor for escalation'
        ]
    }
    return actions.get(anomaly_type, ['Investigate further', 'Monitor ongoing activity'])


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log analysis with progress updates.

    Receives file content and sends back:
    - Progress updates during processing
    - Final analysis results
    - Error messages if something fails
    """
    start_time = time.time()
    await websocket.accept()
    
    try:
        # Set timeout for receiving data (30 seconds)
        try:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
        except asyncio.TimeoutError:
            await websocket.send_json({
                "status": "error",
                "message": "Timeout waiting for file data"
            })
            return

        # For pcapng files, we expect base64 encoded binary content
        file_content_b64 = data.get("content", "")
        
        if not file_content_b64:
            await websocket.send_json({
                "status": "error",
                "message": "No file content received"
            })
            return

        # Decode base64 content to binary
        try:
            import base64
            file_content = base64.b64decode(file_content_b64)
        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "message": "Failed to decode file content. Please ensure the file is properly encoded."
            })
            return

        # Check content size
        content_size_mb = len(file_content) / (1024 * 1024)
        if content_size_mb > 500:
            await websocket.send_json({
                "status": "error",
                "message": f"Content too large: {content_size_mb:.1f}MB. Maximum is 500MB."
            })
            return

        logger.info(f"Starting analysis of {content_size_mb:.2f}MB pcapng content")

        # Initialize components with error handling
        try:
            parser = LogParser()
            detector = AnomalyDetector()
            llm = GemmaClient()
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            await websocket.send_json({
                "status": "error",
                "message": "Failed to initialize analysis components"
            })
            return

        # Step 1: Parse logs (20% progress)
        await websocket.send_json({
            "status": "parsing",
            "progress": 20,
            "message": "Parsing log file..."
        })

        try:
            parsed_logs = await parser.parse(file_content)

            if not parsed_logs:
                await websocket.send_json({
                    "status": "error",
                    "message": "No valid log entries found. Please check the file format. Supported formats: tcpdump, Wireshark CSV, Cisco router logs."
                })
                return

            logger.info(f"Parsed {len(parsed_logs)} log entries")

        except ValueError as e:
            logger.error(f"Parsing failed: {e}")
            await websocket.send_json({
                "status": "error",
                "message": f"Failed to parse log file: {str(e)}"
            })
            return
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            await websocket.send_json({
                "status": "error",
                "message": "Unexpected error during log parsing"
            })
            return

        # Step 2: Statistical analysis (40% progress)
        await websocket.send_json({
            "status": "analyzing",
            "progress": 40,
            "message": f"Analyzing {len(parsed_logs)} log entries..."
        })

        try:
            baseline = detector.calculate_baseline(parsed_logs)
            suspicious_entries = detector.flag_outliers(parsed_logs, baseline)
            
            logger.info(f"Found {len(suspicious_entries)} suspicious patterns")

        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            await websocket.send_json({
                "status": "error",
                "message": "Failed during statistical analysis"
            })
            return

        # Step 3: LLM analysis (60% progress)
        await websocket.send_json({
            "status": "llm_analysis",
            "progress": 60,
            "message": f"Analyzing {len(suspicious_entries)} suspicious patterns with LLM..."
        })

        try:
            # Set timeout for LLM analysis (10 minutes max)
            llm_results = await asyncio.wait_for(
                llm.analyze_anomalies(suspicious_entries, baseline),
                timeout=600.0
            )
            
            logger.info(f"LLM analysis completed: {llm_results.get('total_anomalies', 0)} anomalies found")

        except asyncio.TimeoutError:
            logger.error("LLM analysis timed out")
            logger.info(f"Using statistical fallback for {len(suspicious_entries)} suspicious entries")
            # Use statistical results with fallback formatting instead of erroring out
            llm_results = format_statistical_anomalies(suspicious_entries)
            llm_results['llm_error'] = 'LLM analysis timed out after 10 minutes'
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            logger.info(f"Using statistical fallback for {len(suspicious_entries)} suspicious entries")
            # Use statistical results with fallback formatting
            llm_results = format_statistical_anomalies(suspicious_entries)
            llm_results['llm_error'] = f'LLM analysis failed: {str(e)}'

        # Check if LLM returned an error or no results despite having suspicious entries
        if (llm_results.get('error') or llm_results.get('total_anomalies', 0) == 0) and len(suspicious_entries) > 0:
            logger.warning(f"LLM returned error or no anomalies despite {len(suspicious_entries)} suspicious entries. Using fallback.")
            # Preserve any existing error message
            existing_error = llm_results.get('error', '')
            llm_results = format_statistical_anomalies(suspicious_entries)
            if existing_error:
                llm_results['llm_error'] = existing_error

        # Step 4: Compile final results (80% progress)
        await websocket.send_json({
            "status": "compiling",
            "progress": 80,
            "message": "Compiling analysis report..."
        })

        # Calculate processing time
        processing_time = time.time() - start_time

        # Merge statistical anomalies with LLM insights
        final_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "file_info": {
                "total_packets": len(parsed_logs),
                "unique_sources": baseline.get('unique_sources', 0),
                "unique_destinations": baseline.get('unique_destinations', 0),
                "content_size_mb": round(content_size_mb, 2)
            },
            "baseline": baseline,
            "statistical_anomalies": len(suspicious_entries),
            "llm_analysis": llm_results,
            "summary": llm_results.get('summary', {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }),
            "anomalies": llm_results.get('anomalies', [])
        }

        # Step 5: Send complete results (100% progress)
        await websocket.send_json({
            "status": "complete",
            "progress": 100,
            "message": f"Analysis complete in {processing_time:.1f} seconds",
            "results": final_results
        })

        logger.info(f"Analysis completed successfully in {processing_time:.2f} seconds")

    except WebSocketDisconnect:
        logger.info("Client disconnected during analysis")

    except Exception as e:
        logger.error(f"Unexpected error in WebSocket handler: {e}")
        try:
            await websocket.send_json({
                "status": "error",
                "message": "An unexpected error occurred during analysis"
            })
        except:
            pass  # Connection may already be closed

    finally:
        try:
            await websocket.close()
        except:
            pass  # Already closed


def calculate_estimate(size_mb: float) -> str:
    """
    Calculate estimated processing time based on file size.

    Args:
        size_mb: File size in megabytes

    Returns:
        Human-readable time estimate
    """
    if size_mb < 1:
        return "30 seconds - 1 minute"
    elif size_mb < 10:
        return "1-2 minutes"
    elif size_mb < 50:
        return "2-4 minutes"
    elif size_mb < 100:
        return "4-8 minutes"
    else:
        return "8-15 minutes"


def calculate_estimate_by_packets(packet_count: int) -> str:
    """
    Calculate estimated processing time based on packet count.

    Args:
        packet_count: Number of packets in the pcapng file

    Returns:
        Human-readable time estimate
    """
    if packet_count < 1000:
        return "30 seconds - 1 minute"
    elif packet_count < 10000:
        return "1-2 minutes"
    elif packet_count < 50000:
        return "2-5 minutes"
    elif packet_count < 100000:
        return "5-10 minutes"
    else:
        return "10-20 minutes"


@app.get("/api/test-llm")
async def test_llm_connection():
    """
    Test endpoint to verify LLM connection is working.

    Returns:
        JSON with connection status
    """
    llm = GemmaClient()
    result = await llm.test_connection()
    return result


if __name__ == "__main__":
    import uvicorn
    print("Starting Log Anomaly Analyzer API on port 8000...")
    print("API will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("WebSocket endpoint: ws://localhost:8000/ws/analyze")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
