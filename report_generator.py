# ============================================
# NIDS Project - PDF Report Generator
# Generates professional security report
# from all collected alert data
# ============================================

import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ============================================
# FILE PATHS
# ============================================
ALERTS_JSON = "alerts_log.json"
BLOCKED_JSON = "blocked_ips.json"
OUTPUT_PDF = "NIDS_Security_Report.pdf"

# ============================================
# LOAD DATA
# ============================================
def load_alerts():
    try:
        with open(ALERTS_JSON, "r") as f:
            return json.load(f)
    except:
        return []

def load_blocked_ips():
    try:
        with open(BLOCKED_JSON, "r") as f:
            return json.load(f)
    except:
        return {}

# ============================================
# COLOUR DEFINITIONS
# ============================================
DARK_GREEN = colors.HexColor('#006400')
LIGHT_GREEN = colors.HexColor('#90EE90')
RED = colors.HexColor('#CC0000')
ORANGE = colors.HexColor('#FF8C00')
YELLOW = colors.HexColor('#FFD700')
DARK_GREY = colors.HexColor('#2C2C2C')
LIGHT_GREY = colors.HexColor('#F5F5F5')
WHITE = colors.white
BLACK = colors.black
DARK_RED = colors.HexColor('#8B0000')

# ============================================
# GET SEVERITY COLOUR
# ============================================
def get_severity_color(severity):
    if severity == "CRITICAL":
        return RED
    elif severity == "HIGH":
        return ORANGE
    elif severity == "MEDIUM":
        return YELLOW
    else:
        return LIGHT_GREEN

# ============================================
# GENERATE PDF REPORT
# ============================================
def generate_report():
    print("=" * 55)
    print("   📄 NIDS Security Report Generator")
    print("=" * 55)

    # Load data
    alerts = load_alerts()
    blocked_ips = load_blocked_ips()

    if not alerts:
        print("\n⚠️  No alerts found!")
        print("   Run threat_detector.py first")
        print("   Then run attack_simulator.py")
        print("   Then run this report generator")
        return

    # Calculate statistics
    total_alerts = len(alerts)
    critical = sum(
        1 for a in alerts
        if a.get("severity") == "CRITICAL"
    )
    high = sum(
        1 for a in alerts
        if a.get("severity") == "HIGH"
    )
    medium = sum(
        1 for a in alerts
        if a.get("severity") == "MEDIUM"
    )
    low = sum(
        1 for a in alerts
        if a.get("severity") == "LOW"
    )
    total_blocked = len(blocked_ips)

    # Count alert types
    alert_types = {}
    for alert in alerts:
        t = alert.get("type", "Unknown")
        alert_types[t] = alert_types.get(t, 0) + 1

    # Get unique attacking IPs
    unique_ips = list(set(
        a.get("source_ip", "") for a in alerts
    ))

    print(f"\n✅ Data loaded successfully!")
    print(f"   Total Alerts  : {total_alerts}")
    print(f"   Blocked IPs   : {total_blocked}")
    print(f"\n📄 Generating PDF report...")

    # ============================================
    # CREATE PDF DOCUMENT
    # ============================================
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ============================================
    # HEADER SECTION
    # ============================================

    # Main title
    title_style = styles['Title']
    title_style.fontSize = 24
    title_style.textColor = DARK_GREEN
    title_style.spaceAfter = 5

    story.append(Paragraph(
        "🛡️ NIDS Security Incident Report",
        title_style
    ))

    story.append(Paragraph(
        "Network Intrusion Detection System",
        styles['Normal']
    ))

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=DARK_GREEN
    ))
    story.append(Spacer(1, 0.3*cm))

    # Report metadata table
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_data = [
        ["Report Generated:", now],
        ["Report Type:", "Security Incident Analysis"],
        ["System:", "NIDS v2.0 — Python Based"],
        ["Monitoring Period:", 
         f"{alerts[0].get('timestamp', 'N/A')[:19]} "
         f"to {alerts[-1].get('timestamp', 'N/A')[:19]}"],
        ["Total Events Analysed:", str(total_alerts)],
    ]

    meta_table = Table(meta_data, colWidths=[5*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), DARK_GREEN),
        ('ROWBACKGROUNDS', (0,0), (-1,-1),
         [LIGHT_GREY, WHITE]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # EXECUTIVE SUMMARY
    # ============================================

    story.append(Paragraph(
        "1. Executive Summary",
        styles['Heading1']
    ))

    summary_text = (
        f"This report presents the findings from the NIDS "
        f"monitoring session. The system detected a total of "
        f"<b>{total_alerts} security alerts</b> during the "
        f"monitoring period. Of these, <b>{critical} were "
        f"classified as CRITICAL</b> severity, {high} as HIGH, "
        f"{medium} as MEDIUM, and {low} as LOW severity. "
        f"The automated firewall blocking system successfully "
        f"blocked <b>{total_blocked} malicious IP addresses</b> "
        f"without any human intervention. "
        f"Immediate attention is recommended for all "
        f"CRITICAL and HIGH severity alerts."
    )

    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # STATISTICS SECTION
    # ============================================

    story.append(Paragraph(
        "2. Alert Statistics",
        styles['Heading1']
    ))

    # Stats table
    stats_data = [
        ["Metric", "Count", "Percentage"],
        ["Total Alerts", str(total_alerts), "100%"],
        ["Critical Severity", str(critical),
         f"{round(critical/total_alerts*100, 1)}%"
         if total_alerts > 0 else "0%"],
        ["High Severity", str(high),
         f"{round(high/total_alerts*100, 1)}%"
         if total_alerts > 0 else "0%"],
        ["Medium Severity", str(medium),
         f"{round(medium/total_alerts*100, 1)}%"
         if total_alerts > 0 else "0%"],
        ["Low Severity", str(low),
         f"{round(low/total_alerts*100, 1)}%"
         if total_alerts > 0 else "0%"],
        ["IPs Blocked", str(total_blocked), "Auto-blocked"],
        ["Unique Attackers", str(len(unique_ips)),
         "Distinct IPs"],
    ]

    stats_table = Table(
        stats_data,
        colWidths=[8*cm, 4*cm, 5*cm]
    )
    stats_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), DARK_GREEN),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        # Alternating rows
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [WHITE, LIGHT_GREY]),
        # Severity colours
        ('TEXTCOLOR', (0,2), (-1,2), RED),
        ('TEXTCOLOR', (0,3), (-1,3), ORANGE),
        ('TEXTCOLOR', (0,4), (-1,4), colors.olive),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
    ]))

    story.append(stats_table)
    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # ATTACK TYPES BREAKDOWN
    # ============================================

    story.append(Paragraph(
        "3. Attack Types Detected",
        styles['Heading1']
    ))

    attack_header = [["Attack Type", "Count", "Risk Level"]]
    attack_rows = []

    for alert_type, count in sorted(
        alert_types.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        if "BRUTE FORCE" in alert_type:
            risk = "CRITICAL"
        elif "PORT SCAN" in alert_type:
            risk = "HIGH"
        elif "PING FLOOD" in alert_type:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        attack_rows.append([alert_type, str(count), risk])

    attack_data = attack_header + attack_rows
    attack_table = Table(
        attack_data,
        colWidths=[9*cm, 4*cm, 4*cm]
    )

    attack_style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_GREEN),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [WHITE, LIGHT_GREY]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]

    # Color risk levels
    for i, row in enumerate(attack_rows, 1):
        risk = row[2]
        if risk == "CRITICAL":
            attack_style.append(
                ('TEXTCOLOR', (2,i), (2,i), RED)
            )
        elif risk == "HIGH":
            attack_style.append(
                ('TEXTCOLOR', (2,i), (2,i), ORANGE)
            )
        elif risk == "MEDIUM":
            attack_style.append(
                ('TEXTCOLOR', (2,i), (2,i), colors.olive)
            )

    attack_table.setStyle(TableStyle(attack_style))
    story.append(attack_table)
    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # BLOCKED IPs SECTION
    # ============================================

    story.append(Paragraph(
        "4. Automatically Blocked IP Addresses",
        styles['Heading1']
    ))

    if blocked_ips:
        blocked_header = [[
            "IP Address", "Reason",
            "Blocked At", "Firewall Rule"
        ]]
        blocked_rows = []

        for ip, info in blocked_ips.items():
            blocked_rows.append([
                ip,
                info.get("reason", "N/A"),
                info.get("timestamp", "N/A")[:19],
                info.get("rule_name", "N/A")
            ])

        blocked_data = blocked_header + blocked_rows
        blocked_table = Table(
            blocked_data,
            colWidths=[4*cm, 5*cm, 4.5*cm, 4*cm]
        )
        blocked_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), DARK_RED),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [WHITE, LIGHT_GREY]),
            ('TEXTCOLOR', (0,1), (0,-1), RED),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))

        story.append(blocked_table)
    else:
        story.append(Paragraph(
            "No IPs were blocked during this session.",
            styles['Normal']
        ))

    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # RECENT ALERTS TABLE
    # ============================================

    story.append(Paragraph(
        "5. Recent Alert Log (Last 20)",
        styles['Heading1']
    ))

    recent_alerts = alerts[-20:][::-1]

    alert_header = [[
        "Timestamp", "Alert Type",
        "Source IP", "Severity"
    ]]
    alert_rows = []

    for alert in recent_alerts:
        alert_rows.append([
            alert.get("timestamp", "")[:19],
            alert.get("type", ""),
            alert.get("source_ip", ""),
            alert.get("severity", "")
        ])

    alert_data = alert_header + alert_rows
    alert_table = Table(
        alert_data,
        colWidths=[4.5*cm, 6*cm, 4*cm, 3*cm]
    )

    alert_style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_GREEN),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [WHITE, LIGHT_GREY]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 4),
    ]

    # Color severity column
    for i, row in enumerate(alert_rows, 1):
        sev = row[3]
        if sev == "CRITICAL":
            alert_style.append(
                ('TEXTCOLOR', (3,i), (3,i), RED)
            )
            alert_style.append(
                ('FONTNAME', (3,i), (3,i),
                 'Helvetica-Bold')
            )
        elif sev == "HIGH":
            alert_style.append(
                ('TEXTCOLOR', (3,i), (3,i), ORANGE)
            )

    alert_table.setStyle(TableStyle(alert_style))
    story.append(alert_table)
    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # RECOMMENDATIONS SECTION
    # ============================================

    story.append(Paragraph(
        "6. Security Recommendations",
        styles['Heading1']
    ))

    recommendations = []

    if critical > 0:
        recommendations.append(
            "🔴 CRITICAL: Brute force attacks detected. "
            "Implement account lockout policies and "
            "enable Multi-Factor Authentication (MFA) "
            "on all critical services immediately."
        )

    if any("PORT SCAN" in t for t in alert_types):
        recommendations.append(
            "🟠 HIGH: Port scan activity detected. "
            "Review and restrict firewall rules. "
            "Disable all unnecessary open ports and "
            "implement port knocking for sensitive services."
        )

    if any("PING FLOOD" in t for t in alert_types):
        recommendations.append(
            "🟡 MEDIUM: Ping flood activity detected. "
            "Consider implementing ICMP rate limiting "
            "at the network perimeter firewall."
        )

    recommendations.append(
        "✅ GENERAL: Regularly review and update "
        "firewall rules. Monitor blocked IP list weekly "
        "and report persistent attackers to your ISP."
    )

    recommendations.append(
        "✅ GENERAL: Keep all systems patched and "
        "updated. Enable logging on all network devices "
        "and integrate with a centralized SIEM solution."
    )

    for rec in recommendations:
        story.append(Paragraph(
            f"• {rec}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.5*cm))

    # ============================================
    # FOOTER
    # ============================================

    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=DARK_GREEN
    ))
    story.append(Spacer(1, 0.2*cm))

    footer_text = (
        f"Report generated by NIDS v2.0 | "
        f"Generated on: {now} | "
        f"CONFIDENTIAL — For Internal Use Only"
    )

    footer_style = styles['Normal']
    footer_style.fontSize = 7
    footer_style.textColor = colors.grey
    footer_style.alignment = TA_CENTER

    story.append(Paragraph(footer_text, footer_style))

    # ============================================
    # BUILD PDF
    # ============================================
    doc.build(story)

    print(f"\n✅ Report generated successfully!")
    print(f"📄 File saved as: {OUTPUT_PDF}")
    print(f"📁 Location: {os.path.abspath(OUTPUT_PDF)}")
    print(f"\n   Open the file to view your report!")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    generate_report()