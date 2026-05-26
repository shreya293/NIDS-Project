# ============================================
# NIDS Project - Alert Logger Module
# Description: Saves all alerts permanently
# ============================================

import json
import csv
import os
from datetime import datetime

# ============================================
# FILE NAMES - Where alerts will be saved
# ============================================

LOG_FILE = "alerts_log.txt"      # Human readable log
JSON_FILE = "alerts_log.json"    # Machine readable log
CSV_FILE = "alerts_log.csv"      # Excel readable log

# ============================================
# SETUP - Create files if they don't exist
# ============================================

def setup_logger():
    # Create TXT log file with header
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("   NIDS - Network Intrusion Detection System\n")
            f.write("   Alert Log File\n")
            f.write(f"   Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
    
    # Create JSON log file with empty list
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as f:
            json.dump([], f)
    
    # Create CSV log file with headers
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp",
                "Alert Type", 
                "Source IP",
                "Details",
                "Severity"
            ])
    
    print("✅ Alert logger initialized!")
    print(f"   TXT Log  : {LOG_FILE}")
    print(f"   JSON Log : {JSON_FILE}")
    print(f"   CSV Log  : {CSV_FILE}\n")

# ============================================
# SEVERITY CALCULATOR
# Decides how dangerous each alert is
# ============================================

def get_severity(alert_type):
    if "PORT SCAN" in alert_type:
        return "HIGH"
    elif "BRUTE FORCE" in alert_type:
        return "CRITICAL"
    elif "PING FLOOD" in alert_type:
        return "MEDIUM"
    elif "HTTP FLOOD" in alert_type:
        return "HIGH"
    elif "FTP BRUTE FORCE" in alert_type:
        return "CRITICAL"
    elif "SMTP FLOOD" in alert_type:
        return "MEDIUM"
    else:
        return "LOW"

# ============================================
# MAIN LOGGING FUNCTION
# Call this every time an alert is detected
# ============================================

def log_alert(alert_type, src_ip, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    severity = get_severity(alert_type)
    
    # Build alert dictionary
    alert = {
        "timestamp": timestamp,
        "type": alert_type,
        "source_ip": src_ip,
        "details": details,
        "severity": severity
    }
    
    # ---- Save to TXT file ----
    save_to_txt(alert)
    
    # ---- Save to JSON file ----
    save_to_json(alert)
    
    # ---- Save to CSV file ----
    save_to_csv(alert)
    
    # ---- Print confirmation ----
    print(f"💾 Alert saved! [{severity}] {alert_type} from {src_ip}")
    
    return alert

# ============================================
# SAVE TO TXT - Human readable format
# ============================================

def save_to_txt(alert):
    with open(LOG_FILE, "a") as f:
        f.write(f"ALERT #{get_alert_count()}\n")
        f.write(f"Timestamp : {alert['timestamp']}\n")
        f.write(f"Type      : {alert['type']}\n")
        f.write(f"Severity  : {alert['severity']}\n")
        f.write(f"Source IP : {alert['source_ip']}\n")
        f.write(f"Details   : {alert['details']}\n")
        f.write("-" * 50 + "\n\n")

# ============================================
# SAVE TO JSON - Machine readable format
# ============================================

def save_to_json(alert):
    try:
        with open(JSON_FILE, "r") as f:
            content = f.read().strip()
            if content:
                existing_alerts = json.loads(content)
            else:
                existing_alerts = []
    except:
        existing_alerts = []
    
    existing_alerts.append(alert)
    
    with open(JSON_FILE, "w") as f:
        json.dump(existing_alerts, f, indent=4)
# ============================================
# SAVE TO CSV - Excel readable format
# ============================================

def save_to_csv(alert):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            alert["timestamp"],
            alert["type"],
            alert["source_ip"],
            alert["details"],
            alert["severity"]
        ])

# ============================================
# HELPER - Count total alerts so far
# ============================================

def get_alert_count():
    try:
        with open(JSON_FILE, "r") as f:
            alerts = json.load(f)
            return len(alerts) + 1
    except:
        return 1

# ============================================
# SUMMARY REPORT - Shows all alerts summary
# ============================================

def print_summary():
    try:
        with open(JSON_FILE, "r") as f:
            alerts = json.load(f)
        
        print("\n" + "=" * 60)
        print("   📊 ALERT SUMMARY REPORT")
        print("=" * 60)
        print(f"   Total Alerts    : {len(alerts)}")
        
        # Count by severity
        critical = sum(1 for a in alerts if a["severity"] == "CRITICAL")
        high     = sum(1 for a in alerts if a["severity"] == "HIGH")
        medium   = sum(1 for a in alerts if a["severity"] == "MEDIUM")
        low      = sum(1 for a in alerts if a["severity"] == "LOW")
        
        print(f"   🔴 Critical      : {critical}")
        print(f"   🟠 High          : {high}")
        print(f"   🟡 Medium        : {medium}")
        print(f"   🟢 Low           : {low}")
        
        # Count by type
        print("\n   Alert Types:")
        types = {}
        for alert in alerts:
            t = alert["type"]
            types[t] = types.get(t, 0) + 1
        
        for alert_type, count in types.items():
            print(f"   → {alert_type}: {count} times")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error reading log: {e}")

# ============================================
# TEST - Run this file directly to test
# ============================================

if __name__ == "__main__":
    print("Testing Alert Logger...")
    print("-" * 40)
    
    # Initialize logger
    setup_logger()
    
    # Test logging 3 fake alerts
    log_alert("PORT SCAN DETECTED", 
              "192.168.1.100", 
              "Scanned 20 different ports")
    
    log_alert("BRUTE FORCE ATTACK DETECTED", 
              "10.0.0.5", 
              "50 connection attempts in 10 seconds")
    
    log_alert("PING FLOOD DETECTED", 
              "172.16.0.1", 
              "30 pings in 5 seconds")
    
    # Show summary
    print_summary()
    
    print("\n✅ Check your NIDS_Project folder!")
    print("   You should see 3 new files:")
    print("   → alerts_log.txt")
    print("   → alerts_log.json")
    print("   → alerts_log.csv")