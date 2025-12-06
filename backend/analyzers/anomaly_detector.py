from collections import defaultdict, Counter
from typing import List, Dict
import statistics
from datetime import datetime


class AnomalyDetector:
    """
    Detects network anomalies using statistical analysis and pattern matching.

    Detects 6 types of anomalies:
    1. Port scanning
    2. SYN floods
    3. High retransmissions
    4. Connection timeouts/failures
    5. Unusual port usage
    6. Suspicious traffic patterns
    """

    def __init__(self):
        # Detection thresholds
        self.thresholds = {
            'port_scan_count': 20,  # Connections to > 20 ports
            'port_scan_time': 60,   # Within 60 seconds
            'syn_flood_ratio': 3.0, # SYN/ACK ratio > 3
            'retransmit_threshold': 0.05,  # 5% retransmission rate
            'connection_rate': 100,  # > 100 connections per second
            'high_port_threshold': 10000,  # Ports above this are unusual
            'unusual_port_count': 50,  # More than 50 connections to high ports
            'rst_threshold': 0.1,  # 10% RST packets
            'failed_connection_threshold': 20  # More than 20 failed connections
        }

    def calculate_baseline(self, logs: List[Dict]) -> Dict:
        """
        Calculate baseline statistics for normal traffic patterns.

        Args:
            logs: Parsed log entries

        Returns:
            Dictionary containing baseline metrics
        """
        if not logs:
            return {
                'avg_packet_size': 0,
                'median_packet_size': 0,
                'total_packets': 0,
                'unique_sources': 0,
                'unique_destinations': 0,
                'avg_connections_per_host': 0,
                'protocol_distribution': {}
            }

        # Collect packet sizes
        packet_sizes = [log.get('length', 0) for log in logs if log.get('length')]

        # Connection statistics
        connections = defaultdict(set)
        for log in logs:
            src = log.get('source_ip')
            dst = log.get('dest_ip')
            dst_port = log.get('dest_port')
            if src and dst and dst_port:
                connections[src].add((dst, dst_port))

        # Protocol distribution
        protocol_dist = Counter(log.get('protocol', 'TCP') for log in logs)

        return {
            'avg_packet_size': statistics.mean(packet_sizes) if packet_sizes else 0,
            'median_packet_size': statistics.median(packet_sizes) if packet_sizes else 0,
            'total_packets': len(logs),
            'unique_sources': len(set(log.get('source_ip') for log in logs if log.get('source_ip'))),
            'unique_destinations': len(set(log.get('dest_ip') for log in logs if log.get('dest_ip'))),
            'avg_connections_per_host': sum(len(v) for v in connections.values()) / len(connections) if connections else 0,
            'protocol_distribution': dict(protocol_dist)
        }

    def flag_outliers(self, logs: List[Dict], baseline: Dict) -> List[Dict]:
        """
        Flag suspicious entries based on statistical analysis.

        Args:
            logs: Parsed log entries
            baseline: Baseline statistics

        Returns:
            List of suspicious activities detected
        """
        suspicious = []

        # Detect various anomaly types
        port_scans = self.detect_port_scans(logs)
        suspicious.extend(port_scans)

        syn_floods = self.detect_syn_floods(logs)
        suspicious.extend(syn_floods)

        retransmits = self.detect_retransmissions(logs)
        suspicious.extend(retransmits)

        conn_anomalies = self.detect_connection_anomalies(logs, baseline)
        suspicious.extend(conn_anomalies)

        unusual_ports = self.detect_unusual_ports(logs)
        suspicious.extend(unusual_ports)

        suspicious_patterns = self.detect_suspicious_patterns(logs)
        suspicious.extend(suspicious_patterns)

        return suspicious

    def detect_port_scans(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect port scanning behavior.

        Port scanning: One source IP connecting to many ports on same target.

        Args:
            logs: Parsed log entries

        Returns:
            List of port scan anomalies detected
        """
        scans = []

        # Track port attempts: {source_ip: {target_ip: set(ports)}}
        port_attempts = defaultdict(lambda: defaultdict(set))

        for log in logs:
            src_ip = log.get('source_ip')
            dst_ip = log.get('dest_ip')
            dst_port = log.get('dest_port')

            if src_ip and dst_ip and dst_port:
                port_attempts[src_ip][dst_ip].add(dst_port)

        # Check for scanning behavior
        for src_ip, targets in port_attempts.items():
            for dst_ip, ports in targets.items():
                if len(ports) > self.thresholds['port_scan_count']:
                    # Check if ports are sequential (characteristic of scans)
                    sorted_ports = sorted(list(ports))
                    sequential_count = 0
                    for i in range(len(sorted_ports) - 1):
                        if sorted_ports[i+1] - sorted_ports[i] <= 10:  # Within 10 ports
                            sequential_count += 1

                    scans.append({
                        'type': 'port_scan',
                        'severity': 'CRITICAL',
                        'source_ip': src_ip,
                        'target_ip': dst_ip,
                        'ports_scanned': len(ports),
                        'sample_ports': sorted_ports[:10],  # First 10 ports
                        'sequential_scan': sequential_count > len(ports) * 0.5,  # >50% sequential
                        'description': f'Host {src_ip} scanned {len(ports)} ports on {dst_ip}'
                    })

        return scans

    def detect_syn_floods(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect SYN flood attacks.

        SYN flood: High ratio of SYN packets without corresponding ACK responses.

        Args:
            logs: Parsed log entries

        Returns:
            List of SYN flood anomalies detected
        """
        floods = []

        # Count flags per source IP
        flag_counts = defaultdict(lambda: {'SYN': 0, 'SYNACK': 0, 'ACK': 0, 'total': 0})

        for log in logs:
            src_ip = log.get('source_ip')
            flags = log.get('tcp_flags', '')

            if not src_ip or not flags:
                continue

            flag_counts[src_ip]['total'] += 1

            # Count SYN without ACK
            if 'S' in flags and 'A' not in flags:
                flag_counts[src_ip]['SYN'] += 1
            # Count SYN-ACK
            elif 'S' in flags and 'A' in flags:
                flag_counts[src_ip]['SYNACK'] += 1
            # Count ACK only
            elif 'A' in flags and 'S' not in flags:
                flag_counts[src_ip]['ACK'] += 1

        # Check for suspicious ratios
        for src_ip, counts in flag_counts.items():
            # Need significant traffic to assess
            if counts['total'] < 10:
                continue

            # Calculate SYN flood indicators
            if counts['SYNACK'] > 0:
                syn_to_synack_ratio = counts['SYN'] / counts['SYNACK']
            else:
                syn_to_synack_ratio = counts['SYN']  # All SYN, no responses

            if syn_to_synack_ratio > self.thresholds['syn_flood_ratio']:
                floods.append({
                    'type': 'syn_flood',
                    'severity': 'CRITICAL',
                    'source_ip': src_ip,
                    'syn_count': counts['SYN'],
                    'synack_count': counts['SYNACK'],
                    'ratio': round(syn_to_synack_ratio, 2),
                    'description': f'Potential SYN flood from {src_ip}: {counts["SYN"]} SYN packets with only {counts["SYNACK"]} SYN-ACK responses'
                })

        return floods

    def detect_retransmissions(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect high retransmission rates.

        High retransmissions indicate network problems or packet loss.

        Args:
            logs: Parsed log entries

        Returns:
            List of retransmission anomalies detected
        """
        retrans = []

        # Track sequence numbers per connection
        # connection_key: (src_ip, src_port, dst_ip, dst_port)
        connections = defaultdict(lambda: {'sequences': [], 'total': 0, 'retransmissions': 0})

        for log in logs:
            src_ip = log.get('source_ip')
            src_port = log.get('source_port')
            dst_ip = log.get('dest_ip')
            dst_port = log.get('dest_port')
            seq = log.get('seq')

            if not all([src_ip, src_port, dst_ip, dst_port, seq]):
                continue

            conn_key = (src_ip, src_port, dst_ip, dst_port)
            conn = connections[conn_key]

            conn['total'] += 1

            # Check if this sequence number was seen before (retransmission)
            if seq in conn['sequences']:
                conn['retransmissions'] += 1
            else:
                conn['sequences'].append(seq)

        # Check for high retransmission rates
        for conn_key, conn in connections.items():
            if conn['total'] < 10:  # Need enough packets to assess
                continue

            retrans_rate = conn['retransmissions'] / conn['total']

            if retrans_rate > self.thresholds['retransmit_threshold']:
                src_ip, src_port, dst_ip, dst_port = conn_key
                retrans.append({
                    'type': 'high_retransmissions',
                    'severity': 'MEDIUM',
                    'source_ip': src_ip,
                    'source_port': src_port,
                    'dest_ip': dst_ip,
                    'dest_port': dst_port,
                    'retransmission_rate': round(retrans_rate, 3),
                    'total_packets': conn['total'],
                    'retransmissions': conn['retransmissions'],
                    'description': f'High retransmission rate ({retrans_rate:.1%}) between {src_ip}:{src_port} and {dst_ip}:{dst_port}'
                })

        return retrans

    def detect_connection_anomalies(self, logs: List[Dict], baseline: Dict) -> List[Dict]:
        """
        Detect connection timeouts and failures.

        Indicators: High RST packets, many SYN without completion.

        Args:
            logs: Parsed log entries
            baseline: Baseline statistics

        Returns:
            List of connection anomalies detected
        """
        anomalies = []

        # Count RST packets per connection pair
        rst_counts = defaultdict(int)
        total_packets = defaultdict(int)

        # Track incomplete handshakes
        handshakes = defaultdict(lambda: {'SYN': 0, 'SYNACK': 0, 'ACK': 0})

        for log in logs:
            src_ip = log.get('source_ip')
            dst_ip = log.get('dest_ip')
            flags = log.get('tcp_flags', '')

            if not src_ip or not dst_ip:
                continue

            conn_pair = (src_ip, dst_ip)
            total_packets[conn_pair] += 1

            # Count RST packets
            if 'R' in flags:
                rst_counts[conn_pair] += 1

            # Track handshake stages
            if 'S' in flags and 'A' not in flags:
                handshakes[conn_pair]['SYN'] += 1
            elif 'S' in flags and 'A' in flags:
                handshakes[conn_pair]['SYNACK'] += 1
            elif 'A' in flags:
                handshakes[conn_pair]['ACK'] += 1

        # Check for high RST rates
        for conn_pair, rst_count in rst_counts.items():
            total = total_packets[conn_pair]
            if total < 5:  # Need minimum packets
                continue

            rst_rate = rst_count / total

            if rst_rate > self.thresholds['rst_threshold']:
                src_ip, dst_ip = conn_pair
                anomalies.append({
                    'type': 'connection_resets',
                    'severity': 'MEDIUM',
                    'source_ip': src_ip,
                    'dest_ip': dst_ip,
                    'rst_count': rst_count,
                    'total_packets': total,
                    'rst_rate': round(rst_rate, 3),
                    'description': f'High connection reset rate ({rst_rate:.1%}) between {src_ip} and {dst_ip}'
                })

        # Check for failed handshakes
        for conn_pair, counts in handshakes.items():
            # Many SYN but few completed handshakes
            if counts['SYN'] > self.thresholds['failed_connection_threshold']:
                completion_rate = counts['ACK'] / counts['SYN'] if counts['SYN'] > 0 else 0

                if completion_rate < 0.5:  # Less than 50% completion
                    src_ip, dst_ip = conn_pair
                    anomalies.append({
                        'type': 'failed_connections',
                        'severity': 'HIGH',
                        'source_ip': src_ip,
                        'dest_ip': dst_ip,
                        'syn_attempts': counts['SYN'],
                        'completed': counts['ACK'],
                        'completion_rate': round(completion_rate, 3),
                        'description': f'Many failed connection attempts: {counts["SYN"]} SYN packets but only {counts["ACK"]} completed handshakes'
                    })

        return anomalies

    def detect_unusual_ports(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect connections to unusual high-numbered ports.

        Args:
            logs: Parsed log entries

        Returns:
            List of unusual port anomalies detected
        """
        anomalies = []

        # Common ports that are expected
        common_ports = {21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443}

        # Track connections to high ports
        high_port_connections = defaultdict(lambda: {'count': 0, 'ports': set()})

        for log in logs:
            dst_port = log.get('dest_port')
            src_ip = log.get('source_ip')
            dst_ip = log.get('dest_ip')

            if not all([dst_port, src_ip, dst_ip]):
                continue

            # Check for high-numbered ports not in common set
            if dst_port > self.thresholds['high_port_threshold'] and dst_port not in common_ports:
                key = (src_ip, dst_ip)
                high_port_connections[key]['count'] += 1
                high_port_connections[key]['ports'].add(dst_port)

        # Report unusual port usage
        for (src_ip, dst_ip), data in high_port_connections.items():
            if data['count'] > self.thresholds['unusual_port_count']:
                anomalies.append({
                    'type': 'unusual_ports',
                    'severity': 'LOW',
                    'source_ip': src_ip,
                    'dest_ip': dst_ip,
                    'connection_count': data['count'],
                    'unique_ports': len(data['ports']),
                    'sample_ports': sorted(list(data['ports']))[:10],
                    'description': f'Unusual high-port traffic: {data["count"]} connections to high-numbered ports (>{self.thresholds["high_port_threshold"]})'
                })

        return anomalies

    def detect_suspicious_patterns(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect suspicious traffic patterns like beaconing or data exfiltration.

        Args:
            logs: Parsed log entries

        Returns:
            List of suspicious pattern anomalies detected
        """
        patterns = []

        # Detect potential data exfiltration (large outbound transfers)
        outbound_data = defaultdict(lambda: {'bytes': 0, 'connections': 0})

        for log in logs:
            src_ip = log.get('source_ip')
            dst_ip = log.get('dest_ip')
            length = log.get('length', 0)

            if not all([src_ip, dst_ip]):
                continue

            # Assume internal IPs start with 192.168, 10., or 172.16-31
            is_internal_src = self._is_internal_ip(src_ip)
            is_internal_dst = self._is_internal_ip(dst_ip)

            # Outbound traffic: internal source to external destination
            if is_internal_src and not is_internal_dst:
                key = (src_ip, dst_ip)
                outbound_data[key]['bytes'] += length
                outbound_data[key]['connections'] += 1

        # Check for large data transfers
        for (src_ip, dst_ip), data in outbound_data.items():
            # More than 10MB transferred
            if data['bytes'] > 10 * 1024 * 1024:
                patterns.append({
                    'type': 'data_exfiltration',
                    'severity': 'HIGH',
                    'source_ip': src_ip,
                    'dest_ip': dst_ip,
                    'bytes_transferred': data['bytes'],
                    'megabytes': round(data['bytes'] / (1024 * 1024), 2),
                    'connections': data['connections'],
                    'description': f'Large outbound data transfer: {data["bytes"] / (1024 * 1024):.2f} MB from {src_ip} to external IP {dst_ip}'
                })

        return patterns

    def _is_internal_ip(self, ip: str) -> bool:
        """
        Check if an IP address is from private/internal network.

        Args:
            ip: IP address string

        Returns:
            True if internal/private IP, False otherwise
        """
        if ip.startswith('192.168.') or ip.startswith('10.'):
            return True

        # Check for 172.16.0.0 - 172.31.255.255
        if ip.startswith('172.'):
            parts = ip.split('.')
            if len(parts) >= 2:
                try:
                    second_octet = int(parts[1])
                    if 16 <= second_octet <= 31:
                        return True
                except ValueError:
                    pass

        # Localhost
        if ip.startswith('127.'):
            return True

        return False
