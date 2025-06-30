from flask import request, jsonify
from dotenv import load_dotenv
import os
import requests
import base64
import uuid
from src.utils.api_response import ApiResponse
load_dotenv()

raw_secret = os.getenv("PAYMONGO_SECRET_KEY")
encoded_secret = base64.b64encode(raw_secret.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_secret}",
    "Content-Type": "application/json"
}

class PaymentSerice:
    def create_payment(self, amount: float, team_id: str, currency = "PHP", description="Test payment", name="Sample payment", quantity=1):
        try:
            paymongo_amount = int(amount * 100)
            success_url = request.host_url + "payment/after-success"
            cancel_url = request.host_url + "payment/after-cancel"
            
            reference_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

            data = {
                "data": {
                    "attributes": {
                        "line_items": [
                            {
                                "currency": currency,
                                "amount": paymongo_amount,
                                "description": description,
                                "name": name,
                                "quantity": quantity
                            }
                        ],
                        "payment_method_types": ["card", "gcash", "paymaya"],
                        "description": description,
                        "reference_number": reference_number,
                        "send_email_receipt": True,
                        "show_description": True,
                        "show_line_items": True,
                        "cancel_url": cancel_url,
                        "success_url": success_url
                    }
                }
            }

            response = requests.post(
                "https://api.paymongo.com/v1/checkout_sessions",
                json=data,
                headers=headers
            )

            if response.status_code != 201:
                error_data = response.json()
                detail = error_data.get("errors", [{}])[0].get("detail", "Unknown error")
                raise ValueError(detail)

            checkout_url = response.json()["data"]["attributes"]["checkout_url"]
            return ApiResponse.success(payload=checkout_url)
        except Exception as e:
            return ApiResponse.error(str(e))
        
    def after_success(self):
        return "<h2>🎉 Payment successful! Thank you!</h2>"

    def after_cancel(self):
        return "<h2>❌ Payment canceled. Please try again.</h2>"

    def webhook(self):
        payload = request.get_json()
        event_type = payload["data"]["attributes"]["event"]

        if event_type == "checkout_session.payment_successful":
            print("✅ Payment Successful:", payload["data"]["id"])
        elif event_type == "checkout_session.payment_failed":
            print("❌ Payment Failed:", payload["data"]["id"])
        else:
            print("⚠️ Unhandled Event:", event_type)

        return jsonify({"status": "received"}), 200