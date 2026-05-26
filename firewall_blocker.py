# ============================================
# NIDS Project - Firewall Auto-Blocker
# Description: Automatically blocks malicious IPs
# using Windows Firewall
# ============================================

import subprocess
import json
import os
from datetime import datetime

# ============================================
# FILE TO STORE BLOCKED IPs
# ============================================
BLOCKED_IPS_FILE = "blocked_ips.json"

# ============================================
# SETUP - Load previously blocked IPs
# ============================================
def load_blocked_ips():
    if os.path.exists(BLOCKED_IPS_FILE):
        with open(BLOCKED_IPS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_blocked_ips(blocked_ips):
    with open(BLOCKED_IPS_FILE, "w") as f:
        json.dump(blocked_ips, f, indent=4)

# Load blocked IPs into memory
blocked_ips = load_blocked_ips()

# ============================================
# WHITELIST - IPs we should NEVER block
# Add your important IPs here
# ============================================
WHITELIST = [
    "127.0.0.1",
    "192.168.29.1",
    "192.168.29.54",  # Your own PC
    "8.8.8.8",
    "8.8.4.4",
]

# ============================================
# CHECK if IP is already blocked
# ============================================
def is_blocked(ip):
    return ip in blocked_ips

# ============================================
# CHECK if IP is whitelisted
# ============================================
def is_whitelisted(ip):
    # Check exact match
    if ip in WHITELIST:
        return True
    
    # Check if it's a Microsoft/trusted server
    # These are common false positives
    trusted_ranges = [
        "20.189.",    # Microsoft Azure
        "20.42.",     # Microsoft Azure
        "52.104.",    # Microsoft Teams
        "52.182.",    # Microsoft
        "13.107.",    # Microsoft
        "40.104.",    # Microsoft Azure
        "40.74.",     # Microsoft
        "18.97.",     # Microsoft
        "52.168.",    # Microsoft
    ]
    
    for trusted in trusted_ranges:
        if ip.startswith(trusted):
            return True
    
    return False

# ============================================
# BLOCK IP using Windows Firewall
# ============================================
def block_ip(ip, reason):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ---- Check if already blocked ----
    if is_blocked(ip):
        print(f"⚠️  {ip} is already blocked — skipping")
        return False
    
    # ---- Check whitelist ----
    if is_whitelisted(ip):
        print(f"✅ {ip} is whitelisted — NOT blocking (trusted server)")
        return False
    
    # ---- Create Windows Firewall Rule ----
    rule_name = f"NIDS_Block_{ip}"
    
    # This command adds a firewall rule to block the IP
    command = [
        "netsh", "advfirewall", "firewall",
        "add", "rule",
        f"name={rule_name}",
        "dir=in",           # Block incoming traffic
        "action=block",     # Action is to block
        f"remoteip={ip}",   # The IP to block
        "enable=yes"        # Enable the rule immediately
    ]
    
    try:
        # Run the firewall command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # ---- Success! ----
            blocked_ips[ip] = {
                "timestamp": timestamp,
                "reason": reason,
                "rule_name": rule_name
            }
            
            # Save to file
            save_blocked_ips(blocked_ips)
            
            # Print success message
            print("\n" + "🛡️ " * 20)
            print(f"  FIREWALL RULE ADDED!")
            print(f"  Blocked IP  : {ip}")
            print(f"  Reason      : {reason}")
            print(f"  Time        : {timestamp}")
            print(f"  Rule Name   : {rule_name}")
            print("🛡️ " * 20 + "\n")
            
            return True
        
        else:
            print(f"❌ Failed to block {ip}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error blocking {ip}: {e}")
        return False

# ============================================
# UNBLOCK IP - Remove firewall rule
# ============================================
def unblock_ip(ip):
    if not is_blocked(ip):
        print(f"⚠️  {ip} is not in blocked list")
        return False
    
    rule_name = f"NIDS_Block_{ip}"
    
    command = [
        "netsh", "advfirewall", "firewall",
        "delete", "rule",
        f"name={rule_name}"
    ]
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            del blocked_ips[ip]
            save_blocked_ips(blocked_ips)
            print(f"✅ Successfully unblocked {ip}")
            return True
        else:
            print(f"❌ Failed to unblock {ip}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================
# SHOW all currently blocked IPs
# ============================================
def show_blocked_ips():
    print("\n" + "=" * 50)
    print("   🛡️  CURRENTLY BLOCKED IPs")
    print("=" * 50)
    
    if not blocked_ips:
        print("   No IPs currently blocked")
    else:
        for ip, info in blocked_ips.items():
            print(f"\n   IP      : {ip}")
            print(f"   Reason  : {info['reason']}")
            print(f"   Blocked : {info['timestamp']}")
            print(f"   Rule    : {info['rule_name']}")
    
    print("=" * 50 + "\n")

# ============================================
# TEST - Run this file directly to test
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("   Firewall Blocker Test")
    print("=" * 50)
    
    # Test blocking a fake IP
    print("\n[TEST 1] Blocking a test IP...")
    block_ip("10.0.0.99", "TEST - Port Scan Detected")
    
    # Show blocked IPs
    show_blocked_ips()
    
    # Test unblocking
    print("[TEST 2] Unblocking the test IP...")
    unblock_ip("10.0.0.99")
    
    # Show again - should be empty
    show_blocked_ips()
    
    print("✅ Firewall blocker test complete!")