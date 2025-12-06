import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
from scapy.all import rdpcap, TCP, IP, UDP, ICMP
from scapy.layers.inet import _IPOption_HDR


class LogParser:
    """
    Parses pcapng network capture files and extracts TCP/UDP/ICMP packet information.
    
    Uses Scapy to read pcapng files and extract relevant network data for anomaly detection.
    """

    def __init__(self):
        self.supported_protocols = ['TCP', 'UDP', 'ICMP']

    async def parse(self, file_content: bytes) -> List[Dict]:
        """
        Main parsing function for pcapng files.

        Args:
            file_content: Raw pcapng file content as bytes

        Returns:
            List of parsed packet entries as dictionaries
        """
        # Write bytes to temporary file since scapy needs a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pcapng') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Read pcapng file with scapy
            packets = rdpcap(temp_file_path)
            parsed_packets = []

            for i, packet in enumerate(packets):
                try:
                    parsed_packet = self._parse_packet(packet, i)
                    if parsed_packet:
                        parsed_packets.append(parsed_packet)
                except Exception as e:
                    # Skip malformed packets but continue processing
                    continue

            return parsed_packets

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def _parse_packet(self, packet, packet_num: int) -> Optional[Dict]:
        """
        Parse individual packet and extract relevant information.

        Args:
            packet: Scapy packet object
            packet_num: Packet sequence number

        Returns:
            Dictionary with packet information or None if not relevant
        """
        # Only process IP packets
        if not packet.haslayer(IP):
            return None

        ip_layer = packet[IP]
        
        # Extract basic IP information
        packet_info = {
            'packet_num': packet_num,
            'timestamp': datetime.fromtimestamp(float(packet.time)).strftime('%H:%M:%S.%f'),
            'source_ip': ip_layer.src,
            'dest_ip': ip_layer.dst,
            'length': len(packet),
            'ttl': ip_layer.ttl,
            'protocol': self._get_protocol_name(ip_layer.proto),
            'ip_flags': self._parse_ip_flags(ip_layer.flags),
            'fragment_offset': ip_layer.frag
        }

        # Extract protocol-specific information
        if packet.haslayer(TCP):
            tcp_info = self._parse_tcp(packet[TCP])
            packet_info.update(tcp_info)
            packet_info['protocol'] = 'TCP'
            
        elif packet.haslayer(UDP):
            udp_info = self._parse_udp(packet[UDP])
            packet_info.update(udp_info)
            packet_info['protocol'] = 'UDP'
            
        elif packet.haslayer(ICMP):
            icmp_info = self._parse_icmp(packet[ICMP])
            packet_info.update(icmp_info)
            packet_info['protocol'] = 'ICMP'
        else:
            # Other IP protocols
            packet_info['source_port'] = 0
            packet_info['dest_port'] = 0

        return packet_info

    def _parse_tcp(self, tcp_layer) -> Dict:
        """Extract TCP-specific information."""
        return {
            'source_port': tcp_layer.sport,
            'dest_port': tcp_layer.dport,
            'tcp_flags': self._parse_tcp_flags(tcp_layer.flags),
            'seq': tcp_layer.seq,
            'ack': tcp_layer.ack,
            'window': tcp_layer.window,
            'tcp_options': self._parse_tcp_options(tcp_layer.options),
            'payload_size': len(tcp_layer.payload) if tcp_layer.payload else 0
        }

    def _parse_udp(self, udp_layer) -> Dict:
        """Extract UDP-specific information."""
        return {
            'source_port': udp_layer.sport,
            'dest_port': udp_layer.dport,
            'udp_length': udp_layer.len,
            'payload_size': len(udp_layer.payload) if udp_layer.payload else 0,
            'tcp_flags': '',  # UDP doesn't have flags
            'seq': None,
            'ack': None,
            'window': None
        }

    def _parse_icmp(self, icmp_layer) -> Dict:
        """Extract ICMP-specific information."""
        return {
            'source_port': 0,  # ICMP doesn't have ports
            'dest_port': 0,
            'icmp_type': icmp_layer.type,
            'icmp_code': icmp_layer.code,
            'icmp_id': getattr(icmp_layer, 'id', 0),
            'payload_size': len(icmp_layer.payload) if icmp_layer.payload else 0,
            'tcp_flags': '',
            'seq': None,
            'ack': None,
            'window': None
        }

    def _parse_tcp_flags(self, flags) -> str:
        """Convert TCP flags to string representation."""
        flag_str = ''
        if flags & 0x01:  # FIN
            flag_str += 'F'
        if flags & 0x02:  # SYN
            flag_str += 'S'
        if flags & 0x04:  # RST
            flag_str += 'R'
        if flags & 0x08:  # PSH
            flag_str += 'P'
        if flags & 0x10:  # ACK
            flag_str += 'A'
        if flags & 0x20:  # URG
            flag_str += 'U'
        if flags & 0x40:  # ECE
            flag_str += 'E'
        if flags & 0x80:  # CWR
            flag_str += 'C'
        return flag_str

    def _parse_ip_flags(self, flags) -> str:
        """Parse IP flags."""
        flag_str = ''
        if flags & 0x02:  # Don't Fragment
            flag_str += 'DF'
        if flags & 0x01:  # More Fragments
            flag_str += 'MF'
        return flag_str

    def _parse_tcp_options(self, options) -> List[str]:
        """Parse TCP options."""
        option_list = []
        for option in options:
            if isinstance(option, tuple) and len(option) >= 1:
                option_list.append(str(option[0]))
            else:
                option_list.append(str(option))
        return option_list

    def _get_protocol_name(self, proto_num: int) -> str:
        """Convert protocol number to name."""
        protocol_map = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP'
        }
        return protocol_map.get(proto_num, f'PROTO_{proto_num}')

    def detect_format(self, file_content: bytes) -> str:
        """
        Detect if the file is a valid pcapng file.

        Args:
            file_content: Raw file content as bytes

        Returns:
            'pcapng' if valid, 'unknown' otherwise
        """
        # Check for pcapng magic number
        # pcapng files start with Section Header Block (SHB)
        # Magic number: 0x0A0D0D0A (little endian) or 0x0A0D0D0A (big endian)
        if len(file_content) < 8:
            return 'unknown'
        
        # Check for pcapng magic numbers
        magic_le = b'\x0A\x0D\x0D\x0A'  # Little endian
        magic_be = b'\x0A\x0D\x0D\x0A'  # Big endian (same in this case)
        
        if file_content[:4] == magic_le:
            return 'pcapng'
        
        # Also check for pcap magic numbers as fallback
        pcap_magic_le = b'\xD4\xC3\xB2\xA1'
        pcap_magic_be = b'\xA1\xB2\xC3\xD4'
        
        if file_content[:4] in [pcap_magic_le, pcap_magic_be]:
            return 'pcap'
        
        return 'unknown'

    def validate_pcapng_file(self, file_content: bytes) -> bool:
        """
        Validate that the file is a proper pcapng file.

        Args:
            file_content: Raw file content as bytes

        Returns:
            True if valid pcapng file, False otherwise
        """
        try:
            # Try to create a temporary file and read it with scapy
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pcapng') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Attempt to read the file
                packets = rdpcap(temp_file_path)
                return len(packets) > 0
            finally:
                os.unlink(temp_file_path)
                
        except Exception:
            return False

    def get_file_stats(self, file_content: bytes) -> Dict:
        """
        Get basic statistics about the pcapng file.

        Args:
            file_content: Raw file content as bytes

        Returns:
            Dictionary with file statistics
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pcapng') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                packets = rdpcap(temp_file_path)
                
                if not packets:
                    return {'total_packets': 0, 'protocols': {}, 'time_range': None}

                # Count protocols
                protocols = {}
                timestamps = []
                
                for packet in packets:
                    timestamps.append(packet.time)
                    
                    if packet.haslayer(TCP):
                        protocols['TCP'] = protocols.get('TCP', 0) + 1
                    elif packet.haslayer(UDP):
                        protocols['UDP'] = protocols.get('UDP', 0) + 1
                    elif packet.haslayer(ICMP):
                        protocols['ICMP'] = protocols.get('ICMP', 0) + 1
                    else:
                        protocols['OTHER'] = protocols.get('OTHER', 0) + 1

                # Calculate time range
                time_range = None
                if timestamps:
                    start_time = min(timestamps)
                    end_time = max(timestamps)
                    time_range = {
                        'start': datetime.fromtimestamp(start_time).isoformat(),
                        'end': datetime.fromtimestamp(end_time).isoformat(),
                        'duration_seconds': end_time - start_time
                    }

                return {
                    'total_packets': len(packets),
                    'protocols': protocols,
                    'time_range': time_range
                }

            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            return {'error': str(e), 'total_packets': 0, 'protocols': {}, 'time_range': None}
