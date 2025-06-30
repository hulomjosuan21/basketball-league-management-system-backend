import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from dotenv import load_dotenv
import asyncio
load_dotenv()

async def send_verification_email(recipient_email, verify_link, req):
    def send_email():
        sender_email = "hulomjosuanleonardo@gmail.com"
        app_password = "zwrs qwyz idvr uvco"

        host_url = req.host_url.rstrip('/')
        verification_link = f"{host_url}{verify_link}"

        html_content = f"""
        <html>
        <body>
            <h2>Welcome!</h2>
            <p>Click the button below to verify your email:</p>
            <a href="{verification_link}" style="padding:10px 20px; background-color:#4CAF50; color:white; text-decoration:none;">Verify Email</a>
        </body>
        </html>
        """

        message = MIMEText(html_content, "html")
        message["Subject"] = "Verify Your Account"
        message["From"] = sender_email
        message["To"] = recipient_email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully.")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    return await asyncio.to_thread(send_email)