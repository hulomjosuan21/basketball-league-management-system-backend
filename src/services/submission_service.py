import os
import uuid
import base64
import requests
from flask import request, redirect
from dotenv import load_dotenv

from src.extensions import db
from src.models.league_model import LeagueModel, LeagueTeamModel
from src.utils.api_response import ApiResponse

load_dotenv()

raw_secret = os.getenv("PAYMONGO_SECRET_KEY")
encoded_secret = base64.b64encode(f"{raw_secret}:".encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_secret}",
    "Content-Type": "application/json"
}


class SubmissionPaymentService:
    def create_checkout_url(
        self,
        amount: float,
        submission_type: str,
        submission_id: str,
        league_id: str,
        category_id: str = None,
        currency="PHP",
        description="Submission Payment",
        name="League Entry",
        quantity=1
    ):
        paymongo_amount = int(amount * 100)
        base_url = "https://hideously-patient-dolphin.ngrok-free.app"

        success_url = (
            f"{base_url}/payment/submission-success"
            f"?submission_type={submission_type}"
            f"&submission_id={submission_id}"
            f"&amount={amount}"
            f"&league_id={league_id}"
            f"&category_id={category_id}"
        )
        cancel_url = f"{base_url}/payment-cancelled"

        reference_number = f"SUB-{uuid.uuid4().hex[:8].upper()}"

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

        if response.status_code not in [200, 201]:
            detail = response.json().get("errors", [{}])[0].get("detail", "Unknown error")
            raise Exception(detail)

        return response.json()["data"]["attributes"]["checkout_url"]

class SubmissionPaymentController:
    def __init__(self):
        self.service = SubmissionPaymentService()

    def start_submission_payment(self):
        data = request.get_json() or {}

        submission_type = data.get("submission_type")
        submission_id = data.get("submission_id")
        league_id = data.get("league_id")
        category_id = data.get("category_id")
        amount = data.get("amount")

        if not all([submission_type, submission_id, league_id, amount]):
            raise ValueError("Missing required fields")

        try:
            if submission_type == "team":
                existing = LeagueTeamModel.query.filter_by(
                    team_id=submission_id,
                    league_id=league_id,
                ).first()

                if existing:
                    if existing.payment_status in ["Paid Online", "Paid On Site", "Waived"]:
                        return ApiResponse.error("This team has already paid.", 400)

            checkout_url = self.service.create_checkout_url(
                amount=float(amount),
                submission_type=submission_type,
                submission_id=submission_id,
                league_id=league_id,
                category_id=category_id
            )

            return ApiResponse.success(
                message="Redirect to payment",
                redirect=checkout_url
            )

        except Exception as e:
            return ApiResponse.error(e)

    def handle_success(self):
        submission_type = request.args.get("submission_type")
        submission_id = request.args.get("submission_id")
        league_id = request.args.get("league_id")
        category_id = request.args.get("category_id")
        amount = request.args.get("amount")

        try:
            amount = float(amount or 0)
        except ValueError:
            return redirect("https://bogoballers.site/app/payment-cancelled")

        try:
            if submission_type == "team":
                league = LeagueModel.query.get(league_id)
                if not league:
                    return redirect("https://bogoballers.site/app/payment-cancelled")

                existing = LeagueTeamModel.query.filter_by(
                    team_id=submission_id,
                    league_id=league_id
                ).first()

                if existing:
                    existing.amount_paid = amount
                    existing.payment_status = "Paid Online"
                else:
                    existing = LeagueTeamModel(
                        team_id=submission_id,
                        league_id=league_id,
                        category_id=category_id,
                        amount_paid=amount,
                        payment_status="Paid Online"
                    )
                    db.session.add(existing)

                db.session.commit()

            return redirect("https://bogoballers.site/app/payment-success")
        except Exception as e:
            db.session.rollback()
            return redirect("https://bogoballers.site/app/payment-cancelled")

    def handle_cancelled(self):
        return redirect("https://bogoballers.site/app/payment-cancelled")

    def webhook(self):
        try:
            payload = request.get_json()
            event_type = payload["data"]["attributes"]["event"]
            return ApiResponse.success(message="Webhook received")
        except Exception as e:
            return ApiResponse.error(e)