#!/usr/bin/env python3
"""
Generate a small, focused PCAPNG file with exactly 2 anomalies for quick testing.

Anomalies included:
1. Port scan (CRITICAL) - 25 ports scanned
2. SYN flood (CRITICAL) - High SYN/ACK ratio

Total packets: ~100 (very fast to process)
Expected analysis time: 5-15 seconds
"""

import os
import random
import time
from datetime import datetime, timedelta
from scapy.all import *
from scapy.utils import wrpcap


def generate_quick_test_pcapng(filename="quick_test.pcapng"):
    """
    Generate a small PCAPNG file with 2 clear anomalies for fast testing.
    
    Args:
        filename: Output filename
    """
    packets = []
    base_time = time.time()
    
    print(f"Generating quick test PCAPNG: {filename}")
    print("Anomalies to detect:")
    print("  1. Port scan (CRITICAL) - 25 ports scanned")
    print("  2. SYN flood (CRITICAL) - High SYN/ACK ratio")
    
    # ANOMALY 1: Port Scan (25 ports - should trigger detection)
    scanner_ip = "192.168.1.100"
    target_ip = "10.0.0.50"
    
    print("\n[1/3] Generating port scan anomaly...")
    for i in range(25):  # 25 ports scanned
        timestamp = base_time + (i * 0.1)  # 100ms between scans
        src_port = 50000 + i
        dst_port = 80 + i
        
        # SYN packet (scan attempt)
        syn_packet = IP(src=scanner_ip, dst=target_ip) / TCP(
            sport=src_port, 
            dport=dst_port, 
            flags="S", 
            seq=random.randint(1000000, 9999999)
        )
        syn_packet.time = timestamp
        packets.append(syn_packet)
        
        # RST response (port closed) - every 3rd port
        if i % 3 == 0:
            rst_packet = IP(src=target_ip, dst=scanner_ip) / TCP(
                sport=dst_port, 
                dport=src_port, 
                flags="R", 
                seq=0
            )
            rst_packet.time = timestamp + 0.005
            packets.append(rst_packet)
    
    # ANOMALY 2: SYN Flood (High SYN/ACK ratio)
    attacker_ip = "203.0.113.99"
    victim_ip = "10.0.0.20"
    victim_port = 80
    
    print("[2/3] Generating SYN flood anomaly...")
    flood_start_time = base_time + 10  # Start 10 seconds later
    
    for i in range(30):  # 30 SYN packets
        timestamp = flood_start_time + (i * 0.02)  # 20ms between packets
        src_port = random.randint(40000, 60000)
        
        # SYN packet from attacker
        syn_packet = IP(src=attacker_ip, dst=victim_ip) / TCP(
            sport=src_port, 
            dport=victim_port, 
            flags="S", 
            seq=random.randint(1000000, 9999999)
        )
        syn_packet.time = timestamp
        packets.append(syn_packet)
        
        # Only occasional SYN-ACK responses (creating high ratio)
        if i % 8 == 0:  # Only 1 in 8 get responses
            synack_packet = IP(src=victim_ip, dst=attacker_ip) / TCP(
                sport=victim_port, 
                dport=src_port, 
                flags="SA", 
                seq=random.randint(1000000, 9999999),
                ack=syn_packet[TCP].seq + 1
            )
            synack_packet.time = timestamp + 0.002
            packets.append(synack_packet)
    
    # Add some normal traffic to make it realistic
    print("[3/3] Adding normal background traffic...")
    normal_start_time = base_time + 20
    
    for i in range(15):  # 15 normal connections
        timestamp = normal_start_time + (i * 0.5)
        client_ip = f"192.168.1.{10 + (i % 5)}"
        server_ip = "10.0.0.5"
        server_port = random.choice([80, 443, 22])
        client_port = 51000 + i
        
        seq1 = random.randint(1000000, 9999999)
        seq2 = random.randint(1000000, 9999999)
        
        # Complete handshake
        syn = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="S", seq=seq1)
        syn.time = timestamp
        packets.append(syn)
        
        synack = IP(src=server_ip, dst=client_ip) / TCP(sport=server_port, dport=client_port, flags="SA", seq=seq2, ack=seq1+1)
        synack.time = timestamp + 0.002
        packets.append(synack)
        
        ack = IP(src=client_ip, dst=server_ip) / TCP(sport=client_port, dport=server_port, flags="A", seq=seq1+1, ack=seq2+1)
        ack.time = timestamp + 0.003
        packets.append(ack)
    
    # Write to PCAPNG file
    print(f"\nWriting {len(packets)} packets to {filename}...")
    wrpcap(filename, packets)
    
    # Show file info
    file_size = os.path.getsize(filename) / 1024
    print(f"✅ Created {filename}")
    print(f"   📊 {len(packets)} packets ({file_size:.1f} KB)")
    print(f"   🎯 2 anomalies to detect:")
    print(f"      - Port scan: {scanner_ip} → {target_ip} (25 ports)")
    print(f"      - SYN flood: {attacker_ip} → {victim_ip} (30 SYNs, few responses)")
    print(f"   ⚡ Expected analysis time: 5-15 seconds")
    
    return filename


def main():
    """Generate the quick test file."""
    print("=" * 60)
    print("  🚀 Quick Test PCAPNG Generator")
    print("=" * 60)
    
    filename = generate_quick_test_pcapng()
    
    print("\n" + "=" * 60)
    print("  ✅ Quick Test File Ready!")
    print("=" * 60)
    print(f"\n📁 Upload {filename} to test the application")
    print("🎯 Should detect exactly 2 CRITICAL anomalies")
    print("⚡ Analysis should complete in 5-15 seconds")
    print("\nExpected findings:")
    print("  1. Port Scan - 192.168.1.100 scanning 25 ports")
    print("  2. SYN Flood - 203.0.113.99 flooding 10.0.0.20")


if __name__ == "__main__":
    main()