# ============================================
# NIDS Project - Packet Capture Module
# Created by: [Your Name]
# Description: Captures live network packets
# ============================================

from scapy.all import sniff, IP, TCP, UDP, ICMP
from datetime import datetime

# ---- This function runs for EVERY packet captured ----
def analyse_packet(packet):

    # Only process packets that have an IP layer
    if IP in packet:

        # Extract basic information
        src_ip = packet[IP].src        # Who is SENDING
        dst_ip = packet[IP].dst        # Who is RECEIVING
        protocol = ""                  # What protocol
        info = ""                      # Extra details

        # Check if it's a TCP packet (websites, SSH, etc.)
        if TCP in packet:
            protocol = "TCP"
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            info = f"Port {src_port} → Port {dst_port}"

        # Check if it's a UDP packet (DNS, streaming, etc.)
        elif UDP in packet:
            protocol = "UDP"
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            info = f"Port {src_port} → Port {dst_port}"

        # Check if it's an ICMP packet (ping)
        elif ICMP in packet:
            protocol = "ICMP (Ping)"
            info = "Ping packet detected"

        # Only print if we identified the protocol
        if protocol:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {protocol} | {src_ip} → {dst_ip} | {info}")

# ============================================
# MAIN - Start capturing packets
# ============================================
print("=" * 60)
print("   NIDS - Network Intrusion Detection System")
print("   Packet Capture Started...")
print("   Press CTRL+C to stop")
print("=" * 60)

# Start sniffing - count=50 means capture 50 packets then stop
sniff(prn=analyse_packet, count=50, store=False)

print("\n✅ Capture complete! 50 packets analysed.")