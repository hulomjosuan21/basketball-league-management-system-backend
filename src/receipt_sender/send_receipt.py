import os
import smtplib
import datetime
import pdfkit
from jinja2 import Template
from email.message import EmailMessage
from dotenv import load_dotenv
import uuid

load_dotenv()

class ReceiptSender:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=465):
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        self.logo_url = os.getenv("RECEIPT_LOGO_URL")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def render_receipt_html(self, receipt_data):
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        template_path = os.path.join(BASE_DIR, "assets", "receipt_template.html")

        with open(template_path, "r") as f:
            template = Template(f.read())

        receipt_data["logo_url"] = self.logo_url
        return template.render(receipt_data)

    def send_html_receipt_email(self, to_email, subject, html_content, plain_text_fallback="Thank you for your payment."):
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.set_content(plain_text_fallback)
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
            smtp.login(self.sender_email, self.sender_password)
            smtp.send_message(msg)

        print(f"✅ HTML receipt sent to {to_email}.")

    def _save_pdf_copy(self, html_content, receipt_id):
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        invoices_dir = os.path.join(BASE_DIR, "invoices")
        os.makedirs(invoices_dir, exist_ok=True)

        pdf_path = os.path.join(invoices_dir, f"{receipt_id}.invoice.pdf")
        pdfkit.from_string(html_content, pdf_path)
        print(f"📄 PDF saved to: {pdf_path}")
        return pdf_path

    def send_receipt(self, to_email, amount, receipt_id=None):
        today = datetime.date.today().strftime("%B %d, %Y")

        if not receipt_id:
            receipt_id = f"BogoBallers-{uuid.uuid4().hex[:8].upper()}"

        receipt_data = {
            "receipt_id": receipt_id,
            "amount": amount,
            "date": today,
        }

        html = self.render_receipt_html(receipt_data)

        subject = "Your Receipt from BogoBallers"
        fallback_text = f"Hi {to_email},\n\nThank you for your payment.\n\n– BogoBallers"

        self.send_html_receipt_email(to_email, subject, html, fallback_text)
        self._save_pdf_copy(html, receipt_id)