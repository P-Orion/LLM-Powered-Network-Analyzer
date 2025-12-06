import random
from datetime import datetime, timedelta


def generate_port_scan_log(count=150):
    """
    Generate tcpdump log with port scanning behavior.

    Simulates an attacker scanning many sequential ports on a target.

    Args:
        count: Number of ports to scan

    Returns:
        String containing tcpdump-formatted log entries
    """
    scanner_ip = "192.168.1.45"
    target_ip = "10.0.0.15"
    start_time = datetime.now().replace(hour=14, minute=25, second=0, microsecond=0)

    logs = []

    for i in range(count):
        timestamp = start_time + timedelta(seconds=i*0.5)
        port = 20 + i
        src_port = 50000 + i

        # SYN packet (scan attempt)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {scanner_ip}.{src_port} > "
            f"{target_ip}.{port}: Flags [S], seq {random.randint(1000000, 9999999)}, "
            f"win 65535, length 0"
        )

        # Occasionally add RST response (port closed)
        if i % 3 == 0:
            timestamp_resp = timestamp + timedelta(milliseconds=5)
            logs.append(
                f"{timestamp_resp.strftime('%H:%M:%S.%f')} IP {target_ip}.{port} > "
                f"{scanner_ip}.{src_port}: Flags [R], seq 0, win 0, length 0"
            )

    return '\n'.join(logs)


def generate_syn_flood_log(count=500):
    """
    Generate tcpdump log with SYN flood attack behavior.

    Simulates a DDoS attack with many SYN packets without completion.

    Args:
        count: Number of SYN packets

    Returns:
        String containing tcpdump-formatted log entries
    """
    attacker_ip = "203.0.113.42"
    target_ip = "10.0.0.20"
    target_port = 80
    start_time = datetime.now().replace(hour=15, minute=10, second=0, microsecond=0)

    logs = []

    for i in range(count):
        timestamp = start_time + timedelta(milliseconds=i*10)  # 10ms between packets
        src_port = random.randint(40000, 60000)

        # SYN packet from attacker
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {attacker_ip}.{src_port} > "
            f"{target_ip}.{target_port}: Flags [S], seq {random.randint(1000000, 9999999)}, "
            f"win 65535, length 0"
        )

        # Occasionally add SYN-ACK response (server trying to respond)
        if i % 5 == 0:
            timestamp_resp = timestamp + timedelta(milliseconds=2)
            logs.append(
                f"{timestamp_resp.strftime('%H:%M:%S.%f')} IP {target_ip}.{target_port} > "
                f"{attacker_ip}.{src_port}: Flags [S,A], seq {random.randint(1000000, 9999999)}, "
                f"ack 1, win 29200, length 0"
            )
            # But attacker never completes handshake (no final ACK)

    return '\n'.join(logs)


def generate_clean_log(count=200):
    """
    Generate clean normal TCP traffic log.

    Simulates legitimate client-server communication with complete handshakes.

    Args:
        count: Number of connection sequences

    Returns:
        String containing tcpdump-formatted log entries
    """
    client_ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13"]
    server_ips = ["10.0.0.5", "10.0.0.6"]
    ports = [80, 443, 22, 8080]

    start_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    logs = []

    for i in range(count):
        timestamp = start_time + timedelta(seconds=i*2)  # One connection every 2 seconds
        client_ip = random.choice(client_ips)
        server_ip = random.choice(server_ips)
        server_port = random.choice(ports)
        client_port = 50000 + i

        seq1 = random.randint(1000000, 9999999)
        seq2 = random.randint(1000000, 9999999)

        # Complete 3-way handshake
        # 1. Client sends SYN
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
            f"{server_ip}.{server_port}: Flags [S], seq {seq1}, win 65535, length 0"
        )

        # 2. Server responds with SYN-ACK
        timestamp = timestamp + timedelta(milliseconds=2)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {server_ip}.{server_port} > "
            f"{client_ip}.{client_port}: Flags [S,A], seq {seq2}, ack {seq1+1}, "
            f"win 29200, length 0"
        )

        # 3. Client completes with ACK
        timestamp = timestamp + timedelta(milliseconds=1)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
            f"{server_ip}.{server_port}: Flags [A], ack {seq2+1}, win 65535, length 0"
        )

        # 4. Data transfer (PSH-ACK)
        timestamp = timestamp + timedelta(milliseconds=5)
        data_size = random.randint(100, 1500)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
            f"{server_ip}.{server_port}: Flags [P,A], seq {seq1+1}:{seq1+1+data_size}, "
            f"ack {seq2+1}, win 65535, length {data_size}"
        )

        # 5. Server ACKs data
        timestamp = timestamp + timedelta(milliseconds=2)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {server_ip}.{server_port} > "
            f"{client_ip}.{client_port}: Flags [A], ack {seq1+1+data_size}, "
            f"win 29200, length 0"
        )

        # 6. Connection close with FIN
        timestamp = timestamp + timedelta(milliseconds=100)
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
            f"{server_ip}.{server_port}: Flags [F,A], seq {seq1+1+data_size}, "
            f"ack {seq2+1}, win 65535, length 0"
        )

    return '\n'.join(logs)


def generate_high_retransmission_log(count=100):
    """
    Generate log with high retransmission rate.

    Simulates network issues causing packet retransmissions.

    Args:
        count: Number of connection attempts

    Returns:
        String containing tcpdump-formatted log entries
    """
    client_ip = "192.168.1.20"
    server_ip = "10.0.0.15"
    server_port = 443
    start_time = datetime.now().replace(hour=11, minute=30, second=0, microsecond=0)

    logs = []

    for i in range(count):
        timestamp = start_time + timedelta(seconds=i*0.5)
        client_port = 50100 + i
        seq = random.randint(1000000, 9999999)

        # Original packet
        logs.append(
            f"{timestamp.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
            f"{server_ip}.{server_port}: Flags [P,A], seq {seq}:{seq+500}, "
            f"ack 1, win 65535, length 500"
        )

        # Retransmission (same sequence number) - 30% of packets
        if random.random() < 0.3:
            timestamp_retrans = timestamp + timedelta(milliseconds=200)
            logs.append(
                f"{timestamp_retrans.strftime('%H:%M:%S.%f')} IP {client_ip}.{client_port} > "
                f"{server_ip}.{server_port}: Flags [P,A], seq {seq}:{seq+500}, "
                f"ack 1, win 65535, length 500"
            )

    return '\n'.join(logs)


def main():
    """
    Generate all test log files.
    """
    print("Generating test log files...")

    # Test file 1: Port scan
    with open('test_port_scan.log', 'w') as f:
        f.write(generate_port_scan_log(150))
    print("[OK] Created test_port_scan.log (150 ports scanned)")

    # Test file 2: SYN flood
    with open('test_syn_flood.log', 'w') as f:
        f.write(generate_syn_flood_log(500))
    print("[OK] Created test_syn_flood.log (500 SYN packets)")

    # Test file 3: Clean traffic
    with open('test_clean.log', 'w') as f:
        f.write(generate_clean_log(200))
    print("[OK] Created test_clean.log (200 clean connections)")

    # Test file 4: High retransmissions
    with open('test_retransmissions.log', 'w') as f:
        f.write(generate_high_retransmission_log(100))
    print("[OK] Created test_retransmissions.log (30% retransmission rate)")

    print("\n[SUCCESS] All test files generated successfully!")
    print("\nTest files created:")
    print("  - test_port_scan.log       (Port scanning attack)")
    print("  - test_syn_flood.log       (SYN flood DDoS attack)")
    print("  - test_clean.log           (Normal legitimate traffic)")
    print("  - test_retransmissions.log (Network performance issues)")


if __name__ == "__main__":
    main()
