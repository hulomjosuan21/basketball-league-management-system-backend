from flask import Blueprint
from src.services.submission_service import SubmissionPaymentController

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")
controller = SubmissionPaymentController()

payment_bp.post("/start")(controller.start_submission_payment)
payment_bp.get("/submission-success")(controller.handle_success)
payment_bp.get("/submission-cancelled")(controller.handle_cancelled)
payment_bp.post("/webhook")(controller.webhook)
