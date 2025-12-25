# backend/utils/email_service.py
"""
Email service for sending verification, password reset, and notification emails
Uses Resend API (free tier: 3000 emails/month)
"""
import resend
from typing import Optional
from config import settings
from datetime import datetime

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY

class EmailService:
    """Email service for sending various types of emails"""
    
    @staticmethod
    def send_verification_email(email: str, username: str, verification_token: str) -> bool:
        """
        Send email verification email
        
        Args:
            email: Recipient email address
            username: User's username
            verification_token: Verification token
        
        Returns:
            True if email sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 Welcome to iOps!</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>Thank you for signing up for iOps - Your AI-Powered Data Science Copilot!</p>
                    <p>Please verify your email address by clicking the button below:</p>
                    <center>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </center>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #e5e7eb; padding: 10px; border-radius: 5px; word-break: break-all;">{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't create an account with iOps, please ignore this email.</p>
                    <p>Best regards,<br>The iOps Team</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} iOps. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            params = {
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": "Verify your iOps account",
                "html": html_content,
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Verification email sent to {email}")
            return True
        except Exception as e:
            print(f"❌ Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: Recipient email address
            username: User's username
            reset_token: Password reset token
        
        Returns:
            True if email sent successfully
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>We received a request to reset your password for your iOps account.</p>
                    <p>Click the button below to reset your password:</p>
                    <center>
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </center>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #e5e7eb; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_url}</p>
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong><br>
                        This link will expire in 1 hour. If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                    </div>
                    <p>Best regards,<br>The iOps Team</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} iOps. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            params = {
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": "Reset your iOps password",
                "html": html_content,
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Password reset email sent to {email}")
            return True
        except Exception as e:
            print(f"❌ Error sending password reset email: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email: str, username: str) -> bool:
        """
        Send welcome email after successful verification
        
        Args:
            email: Recipient email address
            username: User's username
        
        Returns:
            True if email sent successfully
        """
        dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #9333ea 0%, #3b82f6 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #9333ea; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to iOps!</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>Your email has been verified successfully! You're all set to start analyzing your data with AI-powered insights.</p>
                    
                    <h3>🚀 Get Started:</h3>
                    <div class="feature">
                        <strong>1. Upload Your Data</strong><br>
                        Support for CSV, Excel, and JSON files up to 50MB
                    </div>
                    <div class="feature">
                        <strong>2. Get AI Insights</strong><br>
                        Automatic analysis and intelligent recommendations
                    </div>
                    <div class="feature">
                        <strong>3. Chat with Sight</strong><br>
                        Ask questions about your data in natural language
                    </div>
                    <div class="feature">
                        <strong>4. Generate Reports</strong><br>
                        Professional PDF reports in seconds
                    </div>
                    
                    <center>
                        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                    </center>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    <p>Happy analyzing!<br>The iOps Team</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} iOps. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            params = {
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": "Welcome to iOps - Let's Get Started!",
                "html": html_content,
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Welcome email sent to {email}")
            return True
        except Exception as e:
            print(f"❌ Error sending welcome email: {str(e)}")
            return False

# Create singleton instance
email_service = EmailService()
