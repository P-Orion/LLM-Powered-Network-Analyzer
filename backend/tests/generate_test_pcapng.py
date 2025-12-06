#!/usr/bin/env python3
"""
Generate test pcapng files for testing the Network Log Analyzer.

This script creates various pcapng files with different network anomalies:
- Port scanning attack
- SYN flood attack  
- Normal traffic
- High retransmission scenario
"""

import os
import random
from datetime import datetime, timedelta
from scapy.all import *
from scapy.utils import wrpcap


def generate_port_scan_pcapng(filename="test_port_scan.pcapng", target_ports=150):
    """
    Generate a pcapng file with port scanning behavior.
    
    Args:
        filename: Output filename
        target_ports: Number of ports to scan
    """
    packets = []
    scanner_ip = "192.168.1.45"
    target_ip = "10.0.0.15"
    base_time = time.time()
    
    print(f"Generating port scan pcapng with {target_ports} ports...")
    
    for i in range(target_ports):
        # Create SYN packet for port scan
        src_port = 50000 + i
        dst_port = 20 + i
        
        # SYN packet
        syn_packet = IP(src=scanner_ip, dst=target_ip) / TCP(sport=src_port, dport=dst_port, flags="S", seq=random.randint(1000000, 9999999))
        syn_packet.time = base_time + (i * 0.1)  # 100ms between scans
        packets.append(syn_packet)
        
        # Occasionally add RST response (port closed)
        if i % 3 == 0:
            rst_packet = IP(src=target_ip, dst=scanner_ip) / TCP(sport=dst_port, dport=src_port, flags="R", seq=0)
            rst_packet.time = base_time + (i * 0.1) + 0.005  # 5ms later
            packets.append(rst_packet)
    
    # Write to pcapng file
    wrpcap(filename, packets)
    print(f"✓ Created {filename} with {len(packets)} packets")


def generate_syn_flood_pcapng(filename="test_syn_flood.pcapng", syn_count=500):
    """
    Generate a pcapng file with SYN flood attack behavior.
    
    Args:
        filename: Output filename
        syn_count: Number of SYN packets to generate
    """
    packets = []
    attacker_ip = "203.0.113.42"
    target_ip = "10.0.0.20"
    target_port = 80
    base_time = time.time()
    
    print(f"Generating SYN flood pcapng with {syn_count} SYN packets...")
    
    for i in range(syn_count):
        # Random source port for each SYN
        src_port = random.randint(40000, 60000)
        
        # SYN packet
        syn_packet = IP(src=attacker_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="S", seq=random.randint(1000000, 9999999))
        syn_packet.time = base_time + (i * 0.01)  # 10ms between packets
        packets.append(syn_packet)
        
        # Occasionally add SYN-ACK response (server trying to respond)
        if i % 5 == 0:
            synack_packet = IP(src=target_ip, dst=attacker_ip) / TCP(sport=target_port, dport=src_port, flags="SA", seq=random.randint(1000000, 9999999), ack=syn_packet[TCP].seq + 1)
            synack_packet.time = base_time + (i * 0.01) + 0.002  # 2ms later
            packets.append(synack_packet)
            # Note: No final ACK from attacker (incomplete handshake)
    
    # Write to pcapng file
    wrpcap(filename, packets)
    print(f"✓ Created {filename} with {len(packets)} packets")


def generate_normal_traffic_pcapng(filename="test_normal_traffic.pcapng", connections=100):
    """
    Generate a pcapng file with normal legitimate traffic.
    
    Args:
        filename: Output filename
        connections: Number of complete connections to generate
    """
    packets = []
    client_ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13"]
    server_ips = ["10.0.0.5", "10.0.0.6"]
    server_ports = [80, 443, 22, 8080]
    base_time = time.time()
    
    print(f"Generating normal traffic pcapng with {connections} connections...")
    
    for i in range(connections):
        client_ip = random.choice(client_ips)
        server_ip = random.choice(server_ips)
        server_port = random.choice(server_ports)
        client_port = 50000 + i
        
        connection_start_time = base_time + (i * 2)  # 2 seconds between connections
        
        # Generate complete TCP handshake
        seq1 = random.randint(1000000, 9999999)
        seq2 = random.randint(1000000, 9999999)
        
        # 1. Client SYN
        syn = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="S", seq=seq1)
        syn.time = connection_start_time
        packets.append(syn)
        
        # 2. Server SYN-ACK
        synack = IP(src=server_ip, dst=client_ip) / TCP(sport=server_port, dport=client_port, flags="SA", seq=seq2, ack=seq1+1)
        synack.time = connection_start_time + 0.002
        packets.append(synack)
        
        # 3. Client ACK
        ack = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="A", seq=seq1+1, ack=seq2+1)
        ack.time = connection_start_time + 0.003
        packets.append(ack)
        
        # 4. Data transfer (PSH-ACK)
        data_size = random.randint(100, 1500)
        data_packet = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="PA", seq=seq1+1, ack=seq2+1) / Raw(b"X" * data_size)
        data_packet.time = connection_start_time + 0.005
        packets.append(data_packet)
        
        # 5. Server ACK
        data_ack = IP(src=server_ip, dst=client_ip) / TCP(sport=server_port, dport=client_port, flags="A", seq=seq2+1, ack=seq1+1+data_size)
        data_ack.time = connection_start_time + 0.007
        packets.append(data_ack)
        
        # 6. Connection close (FIN)
        fin = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="FA", seq=seq1+1+data_size, ack=seq2+1)
        fin.time = connection_start_time + 0.1
        packets.append(fin)
        
        # 7. Server FIN-ACK
        fin_ack = IP(src=server_ip, dst=client_ip) / TCP(sport=server_port, dport=client_port, flags="FA", seq=seq2+1, ack=seq1+2+data_size)
        fin_ack.time = connection_start_time + 0.102
        packets.append(fin_ack)
        
        # 8. Final ACK
        final_ack = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="A", seq=seq1+2+data_size, ack=seq2+2)
        final_ack.time = connection_start_time + 0.103
        packets.append(final_ack)
    
    # Write to pcapng file
    wrpcap(filename, packets)
    print(f"✓ Created {filename} with {len(packets)} packets")


def generate_retransmission_pcapng(filename="test_retransmissions.pcapng", connections=50):
    """
    Generate a pcapng file with high retransmission rates.
    
    Args:
        filename: Output filename
        connections: Number of connections with retransmissions
    """
    packets = []
    client_ip = "192.168.1.20"
    server_ip = "10.0.0.15"
    server_port = 443
    base_time = time.time()
    
    print(f"Generating retransmission pcapng with {connections} connections...")
    
    for i in range(connections):
        client_port = 50100 + i
        connection_time = base_time + (i * 0.5)
        seq = random.randint(1000000, 9999999)
        
        # Original data packet
        original = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="PA", seq=seq, ack=1) / Raw(b"X" * 500)
        original.time = connection_time
        packets.append(original)
        
        # 30% chance of retransmission
        if random.random() < 0.3:
            # Retransmission (same sequence number)
            retrans = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="PA", seq=seq, ack=1) / Raw(b"X" * 500)
            retrans.time = connection_time + 0.2  # 200ms later
            packets.append(retrans)
            
            # Sometimes multiple retransmissions
            if random.random() < 0.1:
                retrans2 = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="PA", seq=seq, ack=1) / Raw(b"X" * 500)
                retrans2.time = connection_time + 0.4  # 400ms later
                packets.append(retrans2)
    
    # Write to pcapng file
    wrpcap(filename, packets)
    print(f"✓ Created {filename} with {len(packets)} packets")


def generate_mixed_protocols_pcapng(filename="test_mixed_protocols.pcapng"):
    """
    Generate a pcapng file with mixed protocols (TCP, UDP, ICMP).
    """
    packets = []
    base_time = time.time()
    
    print("Generating mixed protocols pcapng...")
    
    # TCP traffic
    for i in range(20):
        tcp_packet = IP(src="192.168.1.10", dst="10.0.0.5") / TCP(sport=50000+i, dport=80, flags="S")
        tcp_packet.time = base_time + (i * 0.1)
        packets.append(tcp_packet)
    
    # UDP traffic
    for i in range(15):
        udp_packet = IP(src="192.168.1.11", dst="8.8.8.8") / UDP(sport=53000+i, dport=53) / Raw(b"DNS Query")
        udp_packet.time = base_time + 2 + (i * 0.1)
        packets.append(udp_packet)
    
    # ICMP traffic
    for i in range(10):
        icmp_packet = IP(src="192.168.1.12", dst="8.8.8.8") / ICMP(type=8, code=0, id=i)
        icmp_packet.time = base_time + 4 + (i * 0.5)
        packets.append(icmp_packet)
    
    # Write to pcapng file
    wrpcap(filename, packets)
    print(f"✓ Created {filename} with {len(packets)} packets")


def main():
    """Generate all test pcapng files."""
    print("=" * 50)
    print("  Generating Test PCAPNG Files")
    print("=" * 50)
    
    # Create test files
    generate_port_scan_pcapng("test_port_scan.pcapng", 150)
    generate_syn_flood_pcapng("test_syn_flood.pcapng", 500)
    generate_normal_traffic_pcapng("test_normal_traffic.pcapng", 100)
    generate_retransmission_pcapng("test_retransmissions.pcapng", 50)
    generate_mixed_protocols_pcapng("test_mixed_protocols.pcapng")
    
    print("\n" + "=" * 50)
    print("  Test Files Generated Successfully!")
    print("=" * 50)
    print("\nTest files created:")
    print("  📁 test_port_scan.pcapng       - Port scanning attack (150 ports)")
    print("  📁 test_syn_flood.pcapng       - SYN flood DDoS attack (500 SYN packets)")
    print("  📁 test_normal_traffic.pcapng  - Normal legitimate traffic (100 connections)")
    print("  📁 test_retransmissions.pcapng - High retransmission scenario (30% retrans rate)")
    print("  📁 test_mixed_protocols.pcapng - Mixed TCP/UDP/ICMP traffic")
    
    # Show file sizes
    print("\nFile sizes:")
    for filename in ["test_port_scan.pcapng", "test_syn_flood.pcapng", "test_normal_traffic.pcapng", 
                     "test_retransmissions.pcapng", "test_mixed_protocols.pcapng"]:
        if os.path.exists(filename):
            size_kb = os.path.getsize(filename) / 1024
            print(f"  📊 {filename:<30} {size_kb:.1f} KB")
    
    print(f"\n✅ All test files ready for testing the Network Log Analyzer!")
    print("   Upload these files to test different anomaly detection scenarios.")


if __name__ == "__main__":
    main()