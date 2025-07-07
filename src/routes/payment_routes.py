from flask import Blueprint

from src.services.payment_service import PaymentSerice

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

paymentSerice = PaymentSerice()

payment_bp.post('/create-payment')(paymentSerice.create_payment)
payment_bp.get('/after-success')(paymentSerice.after_success)
payment_bp.get('/after-cancel')(paymentSerice.after_cancel)