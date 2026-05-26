# ============================================
# NIDS Project - Live Dashboard v2.0
# Clean version without IP Spoofing
# ============================================

from flask import Flask, render_template_string, send_file
import json
import os

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIDS Live Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Courier New', monospace;
            background-color: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 20px;
            border: 2px solid #00ff00;
            margin-bottom: 15px;
            background-color: #0d1a0d;
        }

        .header h1 {
            font-size: 26px;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }

        .header p {
            color: #888;
            margin-top: 5px;
            font-size: 13px;
        }

        .report-btn {
            text-align: center;
            margin-bottom: 15px;
        }

        .report-btn a {
            background-color: #006400;
            color: #00ff00;
            padding: 10px 30px;
            border: 2px solid #00ff00;
            text-decoration: none;
            font-family: 'Courier New';
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
        }

        .report-btn a:hover {
            background-color: #00ff00;
            color: #0a0a0a;
        }

        .status-bar {
            text-align: center;
            padding: 8px;
            background-color: #0d1a0d;
            border: 1px solid #333;
            margin-bottom: 15px;
            font-size: 12px;
            color: #888;
        }

        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #00ff00;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 15px;
        }

        .stat-card {
            background-color: #0d1a0d;
            border: 1px solid #00ff00;
            padding: 15px;
            text-align: center;
            border-radius: 5px;
        }

        .stat-card .number {
            font-size: 36px;
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }

        .stat-card .label {
            font-size: 11px;
            color: #888;
            margin-top: 5px;
            text-transform: uppercase;
        }

        .stat-card.critical .number {
            color: #ff4444;
            text-shadow: 0 0 10px #ff4444;
        }
        .stat-card.critical { border-color: #ff4444; }

        .stat-card.high .number {
            color: #ff8800;
            text-shadow: 0 0 10px #ff8800;
        }
        .stat-card.high { border-color: #ff8800; }

        .stat-card.blocked .number {
            color: #4444ff;
            text-shadow: 0 0 10px #4444ff;
        }
        .stat-card.blocked { border-color: #4444ff; }

        .section {
            background-color: #0d1a0d;
            border: 1px solid #00ff00;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }

        .section h2 {
            font-size: 14px;
            color: #00ff00;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #333;
            text-transform: uppercase;
        }

        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }

        th {
            text-align: left;
            padding: 8px;
            background-color: #1a2a1a;
            color: #888;
            font-size: 10px;
            text-transform: uppercase;
            border-bottom: 1px solid #333;
        }

        td {
            padding: 8px;
            border-bottom: 1px solid #1a1a1a;
            color: #ccc;
        }

        tr:hover { background-color: #1a2a1a; }

        .badge {
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        }

        .badge.CRITICAL {
            background-color: #4a0000;
            color: #ff4444;
            border: 1px solid #ff4444;
        }

        .badge.HIGH {
            background-color: #3a2000;
            color: #ff8800;
            border: 1px solid #ff8800;
        }

        .badge.MEDIUM {
            background-color: #3a3a00;
            color: #ffff00;
            border: 1px solid #ffff00;
        }

        .badge.LOW {
            background-color: #003a00;
            color: #00ff00;
            border: 1px solid #00ff00;
        }

        .no-data {
            text-align: center;
            color: #444;
            padding: 15px;
            font-size: 12px;
        }
    </style>
</head>

<body>

    <!-- Header -->
    <div class="header">
        <h1>🛡️ NIDS — Network Intrusion Detection System</h1>
        <p>Live Security Dashboard | Auto-refreshes every 5 seconds</p>
    </div>

    <!-- Report Button -->
    <div class="report-btn">
        <a href="/generate_report">📄 Generate PDF Security Report</a>
    </div>

    <!-- Status Bar -->
    <div class="status-bar">
        <span class="status-dot"></span>
        SYSTEM ACTIVE | Last Updated: {{ last_updated }} |
        Total Alerts: {{ total_alerts }} |
        Blocked IPs: {{ total_blocked }}
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="number">{{ total_alerts }}</div>
            <div class="label">Total Alerts</div>
        </div>
        <div class="stat-card critical">
            <div class="number">{{ critical_count }}</div>
            <div class="label">Critical</div>
        </div>
        <div class="stat-card high">
            <div class="number">{{ high_count }}</div>
            <div class="label">High</div>
        </div>
        <div class="stat-card blocked">
            <div class="number">{{ total_blocked }}</div>
            <div class="label">Blocked IPs</div>
        </div>
    </div>

    <!-- Two Column — Recent Alerts + Blocked IPs -->
    <div class="two-col">

        <!-- Recent Alerts -->
        <div class="section">
            <h2>🚨 Recent Alerts (Last 10)</h2>
            {% if alerts %}
            <table>
                <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Source IP</th>
                    <th>Severity</th>
                </tr>
                {% for alert in alerts[-10:]|reverse %}
                <tr>
                    <td>{{ alert.timestamp[11:19] }}</td>
                    <td>{{ alert.type }}</td>
                    <td>{{ alert.source_ip }}</td>
                    <td>
                        <span class="badge {{ alert.severity }}">
                            {{ alert.severity }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <div class="no-data">
                No alerts yet — system monitoring...
            </div>
            {% endif %}
        </div>

        <!-- Blocked IPs -->
        <div class="section">
            <h2>🛡️ Blocked IPs</h2>
            {% if blocked_ips %}
            <table>
                <tr>
                    <th>IP Address</th>
                    <th>Reason</th>
                    <th>Time</th>
                </tr>
                {% for ip, info in blocked_ips.items() %}
                <tr>
                    <td style="color:#ff4444;">{{ ip }}</td>
                    <td>{{ info.reason }}</td>
                    <td>{{ info.timestamp[11:19] }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <div class="no-data">No IPs blocked yet</div>
            {% endif %}
        </div>

    </div>

    <!-- Full Alert Log -->
    <div class="section">
        <h2>📋 Full Alert Log</h2>
        {% if alerts %}
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Alert Type</th>
                <th>Source IP</th>
                <th>Details</th>
                <th>Severity</th>
            </tr>
            {% for alert in alerts|reverse %}
            <tr>
                <td>{{ alert.timestamp }}</td>
                <td>{{ alert.type }}</td>
                <td>{{ alert.source_ip }}</td>
                <td>{{ alert.details }}</td>
                <td>
                    <span class="badge {{ alert.severity }}">
                        {{ alert.severity }}
                    </span>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <div class="no-data">No alerts logged yet</div>
        {% endif %}
    </div>

</body>
</html>
"""

# ============================================
# LOAD DATA
# ============================================
def load_alerts():
    try:
        with open("alerts_log.json", "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            return []
    except:
        return []

def load_blocked_ips():
    try:
        with open("blocked_ips.json", "r") as f:
            return json.load(f)
    except:
        return {}

# ============================================
# DASHBOARD ROUTE
# ============================================
@app.route("/")
def dashboard():
    from datetime import datetime

    alerts = load_alerts()
    blocked_ips = load_blocked_ips()

    total_alerts = len(alerts)
    critical_count = sum(
        1 for a in alerts
        if a.get("severity") == "CRITICAL"
    )
    high_count = sum(
        1 for a in alerts
        if a.get("severity") == "HIGH"
    )
    total_blocked = len(blocked_ips)
    last_updated = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return render_template_string(
        DASHBOARD_HTML,
        alerts=alerts,
        blocked_ips=blocked_ips,
        total_alerts=total_alerts,
        critical_count=critical_count,
        high_count=high_count,
        total_blocked=total_blocked,
        last_updated=last_updated
    )

# ============================================
# PDF REPORT ROUTE
# ============================================
@app.route("/generate_report")
def generate_report_route():
    try:
        from report_generator import generate_report
        generate_report()
        return send_file(
            "NIDS_Security_Report.pdf",
            as_attachment=True
        )
    except Exception as e:
        return f"Error generating report: {e}"

# ============================================
# START
# ============================================
if __name__ == "__main__":
    print("=" * 55)
    print("   🛡️  NIDS Live Dashboard")
    print("=" * 55)
    print("\n✅ Dashboard starting...")
    print("📊 Open your browser and go to:")
    print("\n   👉  http://127.0.0.1:5000\n")
    print("Press CTRL+C to stop dashboard")
    print("=" * 55 + "\n")

    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )