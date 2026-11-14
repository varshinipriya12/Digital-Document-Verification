import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger(__name__)

class EmailService:

    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Internal helper method to send an email using SMTP configuration from .env / Config.
        If SMTP is not configured, logs/prints content for development testing.
        """
        if not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
            logger.info(f"[DEV MODE EMAIL SERVICE] To: {to_email} | Subject: {subject}")
            print(f"\n==================================================")
            print(f"[DEV MODE EMAIL] To: {to_email}")
            print(f"Subject: {subject}")
            if text_content:
                print(f"Content:\n{text_content}")
            print(f"==================================================\n")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = Config.SMTP_FROM_EMAIL
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            if Config.SMTP_PORT == 465:
                server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)
            else:
                server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)
                server.starttls()

            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_FROM_EMAIL, [to_email], msg.as_string())
            server.quit()
            logger.info(f"Email '{subject}' sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email '{subject}' to {to_email}: {e}")
            print(f"\n[DEV FALLBACK EMAIL] To: {to_email} | Subject: {subject} | Error: {e}\n")
            return True

    @staticmethod
    def send_otp_email(to_email: str, otp: str) -> bool:
        """
        Sends a 6-digit One-Time Password (OTP) for password reset.
        Uses SMTP settings from Config (.env).
        """
        subject = "Your Password Reset OTP - Digital Document Verification Portal"
        
        text_content = f"Your Password Reset OTP for account {to_email} is: {otp}. This code is valid for 10 minutes."
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; background: #ffffff; margin: 0 auto; border-radius: 8px; padding: 30px; border: 1px solid #e2e8f0; }}
            .header {{ text-align: center; border-bottom: 2px solid #0F172A; padding-bottom: 15px; margin-bottom: 20px; }}
            .title {{ color: #0F172A; font-size: 20px; font-weight: 700; margin: 0; }}
            .subtitle {{ color: #64748B; font-size: 13px; margin-top: 4px; }}
            .otp-box {{ background: #F8FAFC; border: 2px dashed #0F172A; border-radius: 8px; text-align: center; padding: 20px; margin: 25px 0; }}
            .otp-code {{ font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #D97706; font-family: monospace; }}
            .notice {{ color: #64748B; font-size: 13px; line-height: 1.5; }}
            .footer {{ margin-top: 25px; text-align: center; font-size: 11px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div class="title">🏛️ DIGITAL DOC VERIFY</div>
              <div class="subtitle">Government Services Verification Assistant</div>
            </div>
            <p style="color: #334155; font-size: 15px;">Hello,</p>
            <p style="color: #334155; font-size: 14px; line-height: 1.5;">
              We received a request to reset your password for account <strong>{to_email}</strong>. Use the One-Time Password (OTP) below to complete your reset:
            </p>
            <div class="otp-box">
              <div class="otp-code">{otp}</div>
            </div>
            <p class="notice">
              ⏱️ This OTP is valid for <strong>10 minutes</strong> and can only be used once.<br>
              🔒 If you did not request a password reset, please ignore this email.
            </p>
            <div class="footer">
              Digital Document Verification Assistant • Official Public Verification Portal
            </div>
          </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content, text_content)

    @staticmethod
    def send_signup_confirmation_email(to_email: str, user_name: str = "") -> bool:
        """
        Sends account signup confirmation email automatically upon registration.
        """
        subject = "Account Registration Successful"
        display_name = user_name if user_name else to_email.split("@")[0]

        message_body = "Your account has been successfully registered on Digital Document Verification Portal. You can now sign in using your registered email and password."

        text_content = f"Hello {display_name},\n\n{message_body}\n\nThank you,\nDigital Document Verification Team"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 520px; background: #ffffff; margin: 0 auto; border-radius: 8px; padding: 30px; border: 1px solid #e2e8f0; }}
            .header {{ text-align: center; border-bottom: 2px solid #0F172A; padding-bottom: 15px; margin-bottom: 20px; }}
            .title {{ color: #0F172A; font-size: 20px; font-weight: 700; margin: 0; }}
            .subtitle {{ color: #64748B; font-size: 13px; margin-top: 4px; }}
            .content-box {{ background: #F8FAFC; border-left: 4px solid #10B981; border-radius: 4px; padding: 20px; margin: 20px 0; }}
            .notice {{ color: #334155; font-size: 14px; line-height: 1.6; margin: 0; }}
            .footer {{ margin-top: 25px; text-align: center; font-size: 11px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div class="title">🏛️ DIGITAL DOC VERIFY</div>
              <div class="subtitle">Government Services Verification Assistant</div>
            </div>
            <p style="color: #334155; font-size: 15px;">Hello <strong>{display_name}</strong>,</p>
            <div class="content-box">
              <p class="notice">
                {message_body}
              </p>
            </div>
            <p style="color: #64748B; font-size: 13px; line-height: 1.5;">
              🔒 For your security, never share your account details or credentials with anyone.
            </p>
            <div class="footer">
              Digital Document Verification Assistant • Official Public Verification Portal
            </div>
          </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content, text_content)
