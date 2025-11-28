# alert_system.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime
import pandas as pd
import os

# -------------------------------
# INDUSTRIAL THRESHOLDS (3 PARAMS ONLY)
# -------------------------------
TEMP_LOW = 65
TEMP_HIGH = 75
TEMP_CRIT = 85

VIB_LOW = 3
VIB_HIGH = 5
VIB_CRIT = 7

SPEED_LOW = 1150
SPEED_HIGH = 1250
SPEED_CRIT = 1350


# -------------------------------
# EMAIL ALERT FUNCTION
# -------------------------------
def send_alert_email(recipient, alerts, avg_temp, avg_vibration, avg_speed, status, recommendation):
    """Send alert email to user with machine condition details - HTML formatted"""
    if not recipient:
        print("⚠️ No recipient email provided")
        return False

    smtp_user = os.environ.get("SMTP_USER") or "s9342902@gmail.com"
    smtp_pass = os.environ.get("SMTP_PASS") or "ncjnfjwjkcwfocda"

    # Determine status color and icon
    if status == "CRITICAL":
        status_color = "#dc3545"
        status_icon = "🚨"
        status_bg = "#f8d7da"
    elif status == "High Risk":
        status_color = "#fd7e14"
        status_icon = "⚠️"
        status_bg = "#fff3cd"
    elif status == "Moderate":
        status_color = "#ffc107"
        status_icon = "📋"
        status_bg = "#fff3cd"
    else:
        status_color = "#28a745"
        status_icon = "✅"
        status_bg = "#d4edda"

    # Determine detailed actions based on status
    if status == "CRITICAL":
        subject = "🚨 CRITICAL: Immediate Machine Shutdown Required"
        action_steps = """
IMMEDIATE ACTIONS REQUIRED:
1. STOP the machine immediately - Do not continue operation
2. Isolate power supply and implement lockout/tagout procedures
3. Contact maintenance team urgently
4. Do NOT restart until thorough inspection is complete
5. Document all observations and readings

CRITICAL ISSUES DETECTED:
"""
    elif status == "High Risk":
        subject = "⚠️ HIGH RISK: Urgent Maintenance Required"
        action_steps = """
URGENT ACTIONS REQUIRED (Within 24 Hours):
1. Reduce machine load by 20-30% immediately
2. Schedule emergency maintenance inspection
3. Monitor all parameters every 30 minutes
4. Prepare for potential shutdown if conditions worsen
5. Have replacement parts ready

HIGH PRIORITY ISSUES:
"""
    elif status == "Moderate":
        subject = "📋 MODERATE RISK: Maintenance Recommended"
        action_steps = """
RECOMMENDED ACTIONS (Within 48 Hours):
1. Schedule routine maintenance inspection
2. Monitor machine parameters closely
3. Check lubrication and cooling systems
4. Review recent operational changes
5. Plan for preventive maintenance

MODERATE ISSUES DETECTED:
"""
    else:
        subject = "✅ Machine Health Report - All Normal"
        action_steps = ""
    
    # Build alerts HTML
    alerts_html = ""
    for alert in alerts:
        alerts_html += f'<li style="margin: 8px 0; color: #333;">{alert}</li>'
    
    # Create HTML email body
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold; letter-spacing: 2px;">OPTIMUS-PdM</h1>
                            <p style="margin: 8px 0 0 0; color: #ffffff; font-size: 14px; opacity: 0.95;">AI-Powered Predictive Maintenance Solutions</p>
                        </td>
                    </tr>
                    
                    <!-- Status Banner -->
                    <tr>
                        <td style="background-color: {status_bg}; padding: 20px 40px; border-left: 5px solid {status_color};">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="font-size: 24px; padding-right: 15px;">{status_icon}</td>
                                    <td>
                                        <p style="margin: 0; font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Machine Status</p>
                                        <h2 style="margin: 5px 0 0 0; color: {status_color}; font-size: 24px; font-weight: bold;">{status}</h2>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 30px 40px;">
                            <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.6;">Hello,</p>
                            <p style="margin: 0 0 25px 0; color: #666; font-size: 14px; line-height: 1.6;">Your machine analysis is complete. Please review the details below and take appropriate action.</p>
                            
                            <!-- Sensor Readings -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background-color: #f8f9fa; border-radius: 6px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333; font-size: 16px; font-weight: bold;">📊 Sensor Readings (Average)</h3>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">🌡️ Temperature:</td>
                                                <td style="color: #333; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_temp:.2f}°C</td>
                                            </tr>
                                            <tr style="border-top: 1px solid #e0e0e0;">
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">📳 Vibration:</td>
                                                <td style="color: #333; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_vibration:.2f} mm/s</td>
                                            </tr>
                                            <tr style="border-top: 1px solid #e0e0e0;">
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">⚡ Speed:</td>
                                                <td style="color: #333; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_speed:.2f} RPM</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Alerts Section -->
                            {f'''
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 6px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 12px 0; color: #856404; font-size: 16px; font-weight: bold;">⚠️ Alerts Detected</h3>
                                        <ul style="margin: 0; padding-left: 20px; color: #856404;">
                                            {alerts_html}
                                        </ul>
                                    </td>
                                </tr>
                            </table>
                            ''' if alerts else ''}
                            
                            <!-- Recommendation -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background-color: #e7f3ff; border-left: 4px solid #2196F3; border-radius: 6px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 12px 0; color: #0d47a1; font-size: 16px; font-weight: bold;">💡 Recommendation</h3>
                                        <p style="margin: 0; color: #1565c0; font-size: 14px; line-height: 1.6;">{recommendation}</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Action Steps -->
                            <h3 style="margin: 0 0 15px 0; color: #333; font-size: 16px; font-weight: bold;">📋 What To Do Next</h3>
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 25px;">
"""
    
    # Add specific next steps based on status
    if status == "CRITICAL":
        html_body += """
                                <p style="margin: 0 0 12px 0; color: #dc3545; font-weight: bold; font-size: 15px;">🚨 CRITICAL - Immediate Action Required</p>
                                <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                                    <li><strong>Emergency Response:</strong> Evacuate personnel, implement shutdown procedures, secure work area</li>
                                    <li><strong>Inspection Required:</strong> Check for damage, inspect cooling system and bearings, document findings</li>
                                    <li><strong>Contact Support:</strong> Call maintenance team immediately, report all readings</li>
                                    <li><strong>Do Not Restart:</strong> Machine must remain offline until cleared by supervisor</li>
                                </ol>
"""
    elif status == "High Risk":
        html_body += """
                                <p style="margin: 0 0 12px 0; color: #fd7e14; font-weight: bold; font-size: 15px;">⚠️ HIGH RISK - Urgent Action Within 24 Hours</p>
                                <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                                    <li><strong>Immediate Monitoring:</strong> Check machine every 30 minutes, log all readings</li>
                                    <li><strong>Maintenance Tasks:</strong> Inspect cooling system, check lubrication, verify mounting bolts</li>
                                    <li><strong>Prepare for Service:</strong> Order replacement parts, schedule maintenance window</li>
                                    <li><strong>Escalation:</strong> Shut down immediately if conditions worsen</li>
                                </ol>
"""
    elif status == "Moderate":
        html_body += """
                                <p style="margin: 0 0 12px 0; color: #ffc107; font-weight: bold; font-size: 15px;">📋 MODERATE - Action Within 48 Hours</p>
                                <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                                    <li><strong>Routine Checks:</strong> Perform daily visual inspection, monitor sensor trends</li>
                                    <li><strong>Preventive Maintenance:</strong> Schedule inspection, review maintenance logs</li>
                                    <li><strong>Monitoring:</strong> Continue normal operation, log any changes</li>
                                    <li><strong>Planning:</strong> Schedule next preventive maintenance</li>
                                </ol>
"""
    else:
        html_body += """
                                <p style="margin: 0 0 12px 0; color: #28a745; font-weight: bold; font-size: 15px;">✅ HEALTHY - Continue Normal Operation</p>
                                <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                                    <li><strong>Normal Operation:</strong> Maintain current procedures, continue standard monitoring</li>
                                    <li><strong>Routine Maintenance:</strong> Follow regular schedule, check lubrication weekly</li>
                                    <li><strong>Best Practices:</strong> Monitor readings regularly, report unusual changes</li>
                                    <li><strong>Preventive Care:</strong> Keep maintenance logs updated</li>
                                </ol>
"""
    
    # Close HTML email
    html_body += f"""
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #2c3e50; padding: 30px 40px; text-align: center;">
                            <h3 style="margin: 0 0 15px 0; color: #ffffff; font-size: 18px; font-weight: bold;">OPTIMUS-PdM</h3>
                            <p style="margin: 0 0 15px 0; color: #ecf0f1; font-size: 13px;">AI-Powered Predictive Maintenance Solutions</p>
                            <p style="margin: 0 0 15px 0; color: #ecf0f1; font-size: 13px;">Keeping your machines running at peak performance</p>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                                <tr>
                                    <td align="center">
                                        <a href="http://localhost:5173" style="display: inline-block; padding: 12px 30px; background-color: #667eea; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; margin: 0 5px;">🌐 Visit Dashboard</a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 20px 0 0 0; color: #95a5a6; font-size: 12px;">
                                📧 support@optimus-pdm.com<br>
                                Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    try:
        # Create multipart message
        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject
        msg["From"] = f"Optimus-PdM <{smtp_user}>"
        msg["To"] = recipient
        
        # Attach HTML content
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"📧 Alert email sent to {recipient}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


# -------------------------------
# GENERATE TWO-PAGE PDF REPORT
# -------------------------------
def generate_pdf_report(data, avg_temp, avg_vibration, avg_speed, status, recommendation, alerts):
    """Generate comprehensive two-page PDF report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Save PDF in backend directory
    pdf_path = os.path.join(os.path.dirname(__file__), "report.pdf")
    
    try:
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # ============ PAGE 1 - Main Report ============
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, height - 50, "OPTIMUS-PdM")
        
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 70, "AI-Powered Predictive Maintenance Solutions")
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 100, "Machine Status Report")
        
        # Draw a line
        c.line(50, height - 110, width - 50, height - 110)
        
        # Report Details
        y = height - 140
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Generated: {timestamp}")
        y -= 20
        c.drawString(50, y, f"Machine ID: {data.get('machine_id', 'N/A')}")
        y -= 20
        c.drawString(50, y, f"User: {data.get('email', 'N/A')}")
        y -= 40
        
        # Status Box
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "STATUS:")
        c.setFont("Helvetica-Bold", 14)
        
        # Color code status
        if status == "CRITICAL":
            c.setFillColorRGB(0.8, 0, 0)  # Red
        elif status == "High Risk":
            c.setFillColorRGB(1, 0.5, 0)  # Orange
        elif status == "Moderate":
            c.setFillColorRGB(1, 0.8, 0)  # Yellow
        else:
            c.setFillColorRGB(0, 0.6, 0)  # Green
            
        c.drawString(130, y, status)
        c.setFillColorRGB(0, 0, 0)  # Reset to black
        y -= 40
        
        # Sensor Values
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "SENSOR READINGS (Average)")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Temperature: {avg_temp:.2f} °C")
        y -= 20
        c.drawString(70, y, f"Vibration: {avg_vibration:.2f} mm/s")
        y -= 20
        c.drawString(70, y, f"Speed: {avg_speed:.2f} RPM")
        y -= 35
        
        # Alerts Section
        c.setFont("Helvetica-Bold", 13)
        if alerts:
            c.setFillColorRGB(0.8, 0, 0)
            c.drawString(50, y, "ALERTS DETECTED")
            c.setFillColorRGB(0, 0, 0)
            y -= 25
            
            c.setFont("Helvetica", 10)
            for alert in alerts:
                if y < 100:  # Check if we need more space
                    break
                c.drawString(70, y, f"• {alert}")
                y -= 18
        else:
            c.setFillColorRGB(0, 0.6, 0)
            c.drawString(50, y, "NO ALERTS - Machine Operating Normally")
            c.setFillColorRGB(0, 0, 0)
            y -= 25
        
        y -= 20
        
        # Recommendation
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "RECOMMENDATION")
        y -= 25
        
        c.setFont("Helvetica", 10)
        # Word wrap recommendation
        words = recommendation.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 10) < (width - 120):
                line = test_line
            else:
                c.drawString(70, y, line)
                y -= 18
                line = word + " "
        if line:
            c.drawString(70, y, line)
        
        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 50, "Optimus-PdM - AI-Powered Predictive Maintenance Solutions")
        c.drawString(50, 35, "🌐 http://localhost:5173 | Page 1 of 2")
        
        # ============ PAGE 2 - Maintenance Guide ============
        c.showPage()
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Maintenance & Forecast Insights")
        c.line(50, height - 60, width - 50, height - 60)
        
        y = height - 100
        
        # Forecast Section
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "FORECAST ANALYSIS")
        y -= 25
        
        c.setFont("Helvetica", 10)
        c.drawString(70, y, "• Temperature: Expected to remain stable within normal range")
        y -= 18
        c.drawString(70, y, "• Vibration: Minor fluctuations possible, monitor closely")
        y -= 18
        c.drawString(70, y, "• Speed: Stable operation expected over next 24 hours")
        y -= 35
        
        # Maintenance Checklist
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "MAINTENANCE CHECKLIST")
        y -= 25
        
        c.setFont("Helvetica", 10)
        checklist = [
            "Inspect cooling system and verify fan operation",
            "Check bearing lubrication levels and top up if needed",
            "Recalibrate sensors if readings appear inconsistent",
            "Verify shaft alignment using dial indicator",
            "Check all mounting bolts for proper torque",
            "Inspect belts and couplings for wear",
            "Clean air filters and vents",
            "Review maintenance logs for patterns"
        ]
        
        for item in checklist:
            if y < 150:
                break
            c.drawString(70, y, f"☐ {item}")
            y -= 18
        
        y -= 20
        
        # Safety Notes
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "SAFETY NOTES")
        y -= 25
        
        c.setFont("Helvetica", 10)
        c.drawString(70, y, "• Always follow lockout/tagout procedures before maintenance")
        y -= 18
        c.drawString(70, y, "• Wear appropriate PPE when working on machinery")
        y -= 18
        c.drawString(70, y, "• For critical alerts, contact maintenance team immediately")
        y -= 18
        c.drawString(70, y, "• Keep detailed records of all maintenance activities")
        
        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 50, "This report was auto-generated by Optimus-PdM AI Engine")
        c.drawString(50, 35, "🌐 http://localhost:5173 | Page 2 of 2")
        
        # Save the PDF
        c.save()
        print(f"✅ PDF report generated: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# -------------------------------
# MAIN PROCESS FUNCTION
# -------------------------------
def process_sensor_data(data):
    """
    Process sensor data, generate alerts, send email, and create PDF report
    """
    temp = data.get("temperature", [])
    speed = data.get("speed", [])
    vibration = data.get("vibration", [])
    recipient = data.get("email")
    machine_id = data.get("machine_id", "Unknown")

    # Validate data
    if not temp or not speed or not vibration:
        return {
            "error": "Missing sensor data",
            "status": "Error",
            "alerts": [],
            "recommendation": "Unable to process - insufficient data"
        }

    min_len = min(len(temp), len(speed), len(vibration))
    if min_len == 0:
        return {
            "error": "Empty sensor data",
            "status": "Error",
            "alerts": [],
            "recommendation": "Unable to process - no data points"
        }

    # Create DataFrame
    df = pd.DataFrame({
        "temperature": temp[:min_len],
        "speed": speed[:min_len],
        "vibration": vibration[:min_len]
    })

    # Calculate averages
    avg_temp = df["temperature"].mean()
    avg_speed = df["speed"].mean()
    avg_vibration = df["vibration"].mean()

    alerts = []

    # TEMPERATURE ANALYSIS
    if avg_temp >= TEMP_CRIT:
        alerts.append(f"CRITICAL temperature {avg_temp:.2f}°C")
    elif avg_temp > TEMP_HIGH:
        alerts.append(f"High temperature {avg_temp:.2f}°C")
    elif avg_temp > TEMP_LOW:
        alerts.append(f"Medium temperature {avg_temp:.2f}°C")

    # VIBRATION ANALYSIS
    if avg_vibration >= VIB_CRIT:
        alerts.append(f"CRITICAL vibration {avg_vibration:.2f} mm/s")
    elif avg_vibration > VIB_HIGH:
        alerts.append(f"High vibration {avg_vibration:.2f} mm/s")
    elif avg_vibration > VIB_LOW:
        alerts.append(f"Medium vibration {avg_vibration:.2f} mm/s")

    # SPEED ANALYSIS
    if avg_speed >= SPEED_CRIT:
        alerts.append(f"CRITICAL speed {avg_speed:.0f} RPM")
    elif avg_speed > SPEED_HIGH:
        alerts.append(f"High speed {avg_speed:.0f} RPM")
    elif avg_speed > SPEED_LOW:
        alerts.append(f"Medium speed {avg_speed:.0f} RPM")

    # DETERMINE STATUS + RECOMMENDATION
    if any("CRITICAL" in a for a in alerts):
        status = "CRITICAL"
        recommendation = "🚨 Immediate shutdown recommended. Inspect machine urgently."
    elif any("High" in a for a in alerts):
        status = "High Risk"
        recommendation = "⚠️ Perform urgent maintenance within 24 hours."
    elif any("Medium" in a for a in alerts):
        status = "Moderate"
        recommendation = "Monitor closely. Schedule inspection within 48 hours."
    else:
        status = "Healthy"
        recommendation = "✅ Machine operating normally. Continue standard monitoring."

    # SEND EMAIL ALERT (always send if recipient provided)
    email_sent = False
    
    if alerts and recipient:
        email_sent = send_alert_email(recipient, alerts, avg_temp, avg_vibration, avg_speed, status, recommendation)
    elif recipient and not alerts:
        # Send confirmation email even if healthy - HTML formatted
        try:
            smtp_user = os.environ.get("SMTP_USER") or "s9342902@gmail.com"
            smtp_pass = os.environ.get("SMTP_PASS") or "ncjnfjwjkcwfocda"
            
            html_healthy = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold; letter-spacing: 2px;">OPTIMUS-PdM</h1>
                            <p style="margin: 8px 0 0 0; color: #ffffff; font-size: 14px; opacity: 0.95;">AI-Powered Predictive Maintenance Solutions</p>
                        </td>
                    </tr>
                    
                    <!-- Status Banner -->
                    <tr>
                        <td style="background-color: #d4edda; padding: 20px 40px; border-left: 5px solid #28a745;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="font-size: 24px; padding-right: 15px;">✅</td>
                                    <td>
                                        <p style="margin: 0; font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Machine Status</p>
                                        <h2 style="margin: 5px 0 0 0; color: #28a745; font-size: 24px; font-weight: bold;">{status}</h2>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 30px 40px;">
                            <p style="margin: 0 0 20px 0; color: #333; font-size: 16px; line-height: 1.6;">Hello,</p>
                            <p style="margin: 0 0 25px 0; color: #666; font-size: 14px; line-height: 1.6;">Your machine analysis is complete. All parameters are within normal operating ranges. ✅</p>
                            
                            <!-- Sensor Readings -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background-color: #f8f9fa; border-radius: 6px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333; font-size: 16px; font-weight: bold;">📊 Sensor Readings (Average)</h3>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">🌡️ Temperature:</td>
                                                <td style="color: #28a745; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_temp:.2f}°C <span style="color: #666; font-weight: normal;">Normal</span></td>
                                            </tr>
                                            <tr style="border-top: 1px solid #e0e0e0;">
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">📳 Vibration:</td>
                                                <td style="color: #28a745; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_vibration:.2f} mm/s <span style="color: #666; font-weight: normal;">Normal</span></td>
                                            </tr>
                                            <tr style="border-top: 1px solid #e0e0e0;">
                                                <td style="color: #666; font-size: 14px; padding: 8px 0;">⚡ Speed:</td>
                                                <td style="color: #28a745; font-size: 14px; font-weight: bold; text-align: right; padding: 8px 0;">{avg_speed:.0f} RPM <span style="color: #666; font-weight: normal;">Normal</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Recommendation -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background-color: #e7f3ff; border-left: 4px solid #2196F3; border-radius: 6px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 12px 0; color: #0d47a1; font-size: 16px; font-weight: bold;">💡 Recommendation</h3>
                                        <p style="margin: 0; color: #1565c0; font-size: 14px; line-height: 1.6;">{recommendation}</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Maintenance Checklist -->
                            <h3 style="margin: 0 0 15px 0; color: #333; font-size: 16px; font-weight: bold;">✅ Routine Maintenance Checklist</h3>
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 25px;">
                                <ul style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                                    <li>Check lubrication levels weekly</li>
                                    <li>Inspect cooling system monthly</li>
                                    <li>Verify sensor calibration</li>
                                    <li>Clean air filters regularly</li>
                                    <li>Monitor for unusual sounds or vibrations</li>
                                    <li>Review operational logs</li>
                                    <li>Update maintenance records</li>
                                </ul>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #2c3e50; padding: 30px 40px; text-align: center;">
                            <h3 style="margin: 0 0 15px 0; color: #ffffff; font-size: 18px; font-weight: bold;">OPTIMUS-PdM</h3>
                            <p style="margin: 0 0 15px 0; color: #ecf0f1; font-size: 13px;">AI-Powered Predictive Maintenance Solutions</p>
                            <p style="margin: 0 0 15px 0; color: #ecf0f1; font-size: 13px;">Keeping your machines running at peak performance</p>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                                <tr>
                                    <td align="center">
                                        <a href="http://localhost:5173" style="display: inline-block; padding: 12px 30px; background-color: #667eea; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; margin: 0 5px;">🌐 Visit Dashboard</a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 20px 0 0 0; color: #95a5a6; font-size: 12px;">
                                📧 support@optimus-pdm.com<br>
                                Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            msg = MIMEMultipart('alternative')
            msg["Subject"] = "✅ Machine Health Report - All Normal"
            msg["From"] = f"Optimus-PdM <{smtp_user}>"
            msg["To"] = recipient
            
            html_part = MIMEText(html_healthy, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            print(f"📧 Health report email sent to {recipient}")
            email_sent = True
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error in health report: {e}")
        except Exception as e:
            print(f"❌ Health report email failed: {e}")

    # GENERATE PDF REPORT
    pdf_path = generate_pdf_report(data, avg_temp, avg_vibration, avg_speed, status, recommendation, alerts)

    return {
        "status": status,
        "avg_temp": avg_temp,
        "avg_vibration": avg_vibration,
        "avg_speed": avg_speed,
        "alerts": alerts,
        "recommendation": recommendation,
        "report_url": "/download" if pdf_path else None,
        "email_sent": email_sent,
        "machine_id": machine_id
    }
