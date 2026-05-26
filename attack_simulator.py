# ============================================
# NIDS Project - Attack Simulator v3.0
# Fixed: Better pacing + Working Ping Flood
# ============================================

import socket
import time
import os

# ============================================
# AUTO DETECT OWN IP
# ============================================
def get_own_ip():
    try:
        s = socket.socket(socket.AF_INET,
                          socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ============================================
# WELCOME BANNER
# ============================================
os.system('cls' if os.name == 'nt' else 'clear')

print("=" * 55)
print("   🛡️  NIDS Attack Simulator v3.0")
print("=" * 55)
print()
print("   Simulates real network attacks")
print("   for testing NIDS detection only.")
print()
print("   ⚠️  WARNING: Only scan networks")
print("   you own or have permission to scan!")
print("   Unauthorized scanning is ILLEGAL!")
print("=" * 55)

# ============================================
# DYNAMIC IP SELECTION
# ============================================
own_ip = get_own_ip()

print(f"\n   Your detected IP : {own_ip}")
print("\n   Choose target:")
print(f"   1. Your own machine ({own_ip}) [RECOMMENDED]")
print()

TARGET = own_ip
print(f"\n   ✅ Target set to your machine: {TARGET}")

# ============================================
# ATTACK MENU
# ============================================
print("\n" + "=" * 55)
print("   Choose attack simulation:")
print("   1. Port Scan only")
print("   2. Brute Force only")
print("   3. Ping Flood only")
print("   4. ALL attacks (Full simulation)")
print("=" * 55)

attack_choice = input("\n   Enter choice (1-4): ").strip()

print("\n" + "=" * 55)
print(f"   Target  : {TARGET}")
print("   Starting in 3 seconds...")
print("   Watch your NIDS terminal for alerts!")
print("=" * 55)
time.sleep(3)

# ============================================
# ATTACK 1 — Port Scan
# Scans 6 specific ports slowly
# Triggers PORT SCAN DETECTED
# ============================================
def simulate_port_scan():
    print("\n" + "-" * 45)
    print("[*] PORT SCAN SIMULATION STARTING...")
    print(f"    Target: {TARGET}")
    print(f"    Scanning 6 key ports...")
    print("-" * 45)

    ports_to_scan = [22, 80, 443, 3389, 8080, 21]

    for i, port in enumerate(ports_to_scan, 1):
        try:
            s = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
            s.settimeout(0.5)
            result = s.connect_ex((TARGET, port))
            s.close()
            status = "OPEN" if result == 0 else "CLOSED"
        except:
            status = "FILTERED"

        print(f"    [{i}/6] Port {port:5d} ... {status}")
        time.sleep(1)  # Slow enough to see clearly

    print("\n    ✅ Port Scan Complete!")
    print("    → Check NIDS terminal for PORT SCAN ALERT!")

# ============================================
# ATTACK 2 — Brute Force
# Makes rapid connections to port 445
# Triggers BRUTE FORCE DETECTED
# ============================================
def simulate_brute_force():
    print("\n" + "-" * 45)
    print("[*] BRUTE FORCE SIMULATION STARTING...")
    print(f"    Target: {TARGET}:445 (SMB)")
    print(f"    Making rapid connection attempts...")
    print("-" * 45)

    success = 0
    for i in range(1, 101):
        try:
            s = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
            s.settimeout(0.05)
            s.connect((TARGET, 445))
            s.close()
            success += 1
        except:
            pass

        # Show progress every 10 connections
        if i % 10 == 0:
            print(f"    Attempt {i:3d}/100 — "
                  f"Trying credentials...")

    print(f"\n    ✅ Brute Force Complete!")
    print(f"    Total attempts: 100")
    print("    → Check NIDS terminal for BRUTE FORCE ALERT!")

# ============================================
# ATTACK 3 — Ping Flood (FIXED!)
# Uses TCP rapid connections to port 7
# AND Scapy ICMP as backup
# Triggers PING FLOOD DETECTED
# ============================================
def simulate_ping_flood():
    print("\n" + "-" * 45)
    print("[*] PING FLOOD SIMULATION STARTING...")
    print(f"    Target: {TARGET}")
    print(f"    Sending rapid ping packets...")
    print("-" * 45)

    # Method 1 — Try Scapy ICMP first
    try:
        import importlib
        scapy = importlib.import_module("scapy.all")
        IP = scapy.IP
        ICMP = scapy.ICMP
        send = scapy.send
        conf = scapy.conf
        conf.verb = 0  # Suppress Scapy output

        print("    Using Scapy ICMP method...")
        for i in range(1, 51):
            # Send from a DIFFERENT source IP
            # so Scapy captures it properly
            pkt = IP(
                src="10.0.0.1",  # Fake source IP
                dst=TARGET
            ) / ICMP()
            send(pkt, verbose=False)

            if i % 5 == 0:
                print(f"    Sent {i:2d}/50 ICMP packets...")
            time.sleep(0.1)

        print("\n    ✅ Ping Flood Complete (ICMP)!")
        print("    → Check NIDS terminal for PING FLOOD ALERT!")
        return

    except Exception as e:
        print(f"    Scapy ICMP failed: {e}")
        print("    Switching to TCP rapid method...")

    # Method 2 — TCP rapid connections
    # This will trigger BRUTE FORCE on port 7
    # which still demonstrates flood detection
    print("    Using TCP flood method...")
    for i in range(1, 101):
        try:
            s = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
            s.settimeout(0.05)
            s.connect((TARGET, 135))
            s.close()
        except:
            pass

        if i % 10 == 0:
            print(f"    Flood packet {i:3d}/100 sent...")

    print("\n    ✅ Flood Simulation Complete!")
    print("    → Check NIDS terminal for FLOOD ALERT!")

# ============================================
# RUN SELECTED ATTACKS
# ============================================
if attack_choice == "1":
    simulate_port_scan()

elif attack_choice == "2":
    simulate_brute_force()

elif attack_choice == "3":
    simulate_ping_flood()

elif attack_choice == "4":
    simulate_port_scan()
    print("\n   ⏳ Waiting 3 seconds before next attack...")
    time.sleep(3)
    simulate_brute_force()
    print("\n   ⏳ Waiting 3 seconds before next attack...")
    time.sleep(3)
    simulate_ping_flood()
else:
    print("Invalid choice! Running full simulation...")
    simulate_port_scan()
    time.sleep(3)
    simulate_brute_force()

print("\n" + "=" * 55)
print("   ✅ All simulations complete!")
print("   PRESS CTRL+C IN TERMINAL 1 to see summary!")
print("=" * 55)