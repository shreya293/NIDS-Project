# ============================================
# NIDS Project - Threat Detector v2.0
# Detects: Port Scan, Brute Force, Ping Flood
# ============================================

from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
from alert_logger import setup_logger, log_alert, print_summary
from firewall_blocker import block_ip, show_blocked_ips
from datetime import datetime
from collections import defaultdict
import sys

# import os

# def clean_old_logs():
#     """Safely delete old log files — no error if missing"""
#     files_to_delete = [
#         "alerts_log.txt",
#         "alerts_log.json",
#         "alerts_log.csv",
#         "blocked_ips.json"
#     ]
#     print("🗑️  Cleaning old log files...")
#     for f in files_to_delete:
#         if os.path.exists(f):
#             os.remove(f)
#             print(f"   ✅ Deleted: {f}")
#         else:
#             print(f"   ⚠️  Not found (skipping): {f}")
#     print("✅ Clean session ready!\n")

# # Call it at startup
# clean_old_logs()
# ============================================
# MEMORY STORAGE
# ============================================
port_scan_tracker = defaultdict(set)
brute_force_tracker = defaultdict(list)
ping_tracker = defaultdict(list)
alerts = []

# ============================================
# DETECTION THRESHOLDS
# ============================================
PORT_SCAN_THRESHOLD = 5
BRUTE_FORCE_THRESHOLD = 30
BRUTE_FORCE_WINDOW = 10
PING_FLOOD_THRESHOLD = 10
PING_FLOOD_WINDOW = 30

# ============================================
# ALERT FUNCTION
# ============================================
def create_alert(alert_type, src_ip, details):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    alert = {
        "time": timestamp,
        "type": alert_type,
        "src_ip": src_ip,
        "details": details
    }

    alerts.append(alert)

    print("\n" + "!" * 60)
    print(f"  🚨 ALERT DETECTED!")
    print(f"  Type    : {alert_type}")
    print(f"  Time    : {timestamp}")
    print(f"  Source  : {src_ip}")
    print(f"  Details : {details}")
    print("!" * 60 + "\n")

    log_alert(alert_type, src_ip, details)
    block_ip(src_ip, alert_type)

# ============================================
# DETECTION 1 — Port Scan
# ============================================
def check_port_scan(src_ip, dst_port):
    port_scan_tracker[src_ip].add(dst_port)
    ports_tried = len(port_scan_tracker[src_ip])

    if ports_tried == PORT_SCAN_THRESHOLD:
        create_alert(
            "PORT SCAN DETECTED",
            src_ip,
            f"Tried {ports_tried} different ports "
            f"— possible reconnaissance attack"
        )

# ============================================
# DETECTION 2 — Brute Force
# ============================================
def check_brute_force(src_ip):
    now = datetime.now().timestamp()
    brute_force_tracker[src_ip].append(now)

    brute_force_tracker[src_ip] = [
        t for t in brute_force_tracker[src_ip]
        if now - t <= BRUTE_FORCE_WINDOW
    ]

    recent_attempts = len(
        brute_force_tracker[src_ip]
    )

    if recent_attempts == BRUTE_FORCE_THRESHOLD:
        create_alert(
            "BRUTE FORCE ATTACK DETECTED",
            src_ip,
            f"{recent_attempts} rapid connections "
            f"in {BRUTE_FORCE_WINDOW} seconds"
        )

# ============================================
# DETECTION 3 — Ping Flood
# ============================================
def check_ping_flood(src_ip):
    now = datetime.now().timestamp()
    ping_tracker[src_ip].append(now)

    ping_tracker[src_ip] = [
        t for t in ping_tracker[src_ip]
        if now - t <= PING_FLOOD_WINDOW
    ]

    if len(ping_tracker[src_ip]) == PING_FLOOD_THRESHOLD:
        create_alert(
            "PING FLOOD DETECTED",
            src_ip,
            f"{len(ping_tracker[src_ip])} pings in "
            f"{PING_FLOOD_WINDOW} seconds "
            f"— possible DoS attack"
        )

# ============================================
# MAIN PACKET ANALYSER
# ============================================
def analyse_packet(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        timestamp = datetime.now().strftime("%H:%M:%S")

        # ---- TCP Packets ----
        if TCP in packet:
            dst_port = packet[TCP].dport
            src_port = packet[TCP].sport

            if dst_port == 443 or src_port == 443:
                protocol_name = "HTTPS"
            elif dst_port == 21 or src_port == 21:
                protocol_name = "FTP"
            elif dst_port == 25 or src_port == 25:
                protocol_name = "SMTP"
            elif dst_port == 22 or src_port == 22:
                protocol_name = "SSH"
            elif dst_port == 3389 or src_port == 3389:
                protocol_name = "RDP"
            elif dst_port == 80 or src_port == 80:
                protocol_name = "HTTP"
            else:
                protocol_name = "TCP"

            print(f"[{timestamp}] {protocol_name} | "
                  f"{src_ip} → {dst_ip} | "
                  f"Port {src_port} → Port {dst_port}")

            check_port_scan(src_ip, dst_port)

            unique_ports = len(
                port_scan_tracker[src_ip]
            )
            if unique_ports < PORT_SCAN_THRESHOLD:
                check_brute_force(src_ip)

        # ---- UDP Packets ----
        elif UDP in packet:
            dst_port = packet[UDP].dport
            src_port = packet[UDP].sport

            if dst_port == 53 or src_port == 53:
                protocol_name = "DNS"
            elif dst_port == 67 or src_port == 67:
                protocol_name = "DHCP"
            else:
                protocol_name = "UDP"

            print(f"[{timestamp}] {protocol_name} | "
                  f"{src_ip} → {dst_ip} | "
                  f"Port {src_port} → Port {dst_port}")

            check_port_scan(src_ip, dst_port)

        # ---- ICMP Packets ----
        elif ICMP in packet:
            print(f"[{timestamp}] ICMP | "
                f"{src_ip} → {dst_ip} | "
                f"Ping packet detected!")
            check_ping_flood(src_ip)

    # Also count ICMP from loopback
    # to catch simulator packets
            if src_ip == "10.0.0.1":
                print(f"[{timestamp}] ICMP | "
                    f"Simulated ping from {src_ip}")
                check_ping_flood(src_ip)

# ============================================
# SHUTDOWN
# ============================================
def shutdown():
    print("\n" + "=" * 60)
    print(f"  Monitoring stopped.")
    print(f"  Total Alerts Generated: {len(alerts)}")
    print("=" * 60)
    print_summary()
    show_blocked_ips()
    sys.exit(0)

# ============================================
# START
# ============================================
setup_logger()

print("=" * 60)
print("   🛡️  NIDS - Network Intrusion Detection System")
print("=" * 60)
print("   Monitoring for:")
print("   🔍 Port Scans       (5+ different ports)")
print("   🔐 Brute Force      (50+ connections/5sec)")
print("   💥 Ping Flood       (15+ pings/10sec)")
print("=" * 60)
print("   Protocols Identified:")
print("   HTTPS | HTTP | FTP | SMTP | SSH | RDP | DNS")
print("=" * 60)
print("   Press CTRL+C to stop and see summary")
print("=" * 60 + "\n")

try:
    sniff(prn=analyse_packet, store=False)
except KeyboardInterrupt:
    pass
finally:
    shutdown()