# alerts/email_alert.py
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

async def send_alert_email(alert: dict):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 PacketHound Alert — {alert['rule_name']}"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        html = f"""
        <html>
        <body style="background:#0f1117; color:#fff; font-family:sans-serif; padding:24px;">
            <h2 style="color:#ef4444;">🐾 PacketHound Security Alert</h2>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td style="padding:8px; color:#888;">Rule</td><td style="padding:8px;">{alert['rule_name']}</td></tr>
                <tr><td style="padding:8px; color:#888;">Severity</td><td style="padding:8px; color:#ef4444;"><b>{alert['severity']}</b></td></tr>
                <tr><td style="padding:8px; color:#888;">Source IP</td><td style="padding:8px;">{alert['src_ip']}</td></tr>
                <tr><td style="padding:8px; color:#888;">Description</td><td style="padding:8px;">{alert['description']}</td></tr>
                <tr><td style="padding:8px; color:#888;">Time</td><td style="padding:8px;">{alert['timestamp']}</td></tr>
            </table>
            <p style="color:#888; margin-top:24px;">PacketHound 🐾 is watching your network.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=EMAIL_SENDER,
            password=EMAIL_PASSWORD,
        )
        print(f"[📧] Alert email sent for: {alert['rule_name']}")

    except Exception as e:
        print(f"[❌] Email failed: {e}")