from flask import Blueprint

from src.services.notification_serices import NotificationService

notification_bp = Blueprint('notification', __name__, url_prefix='/notification')

notification_bp.get('/fetch-from/<string:user_id>')(NotificationService.fetchNotifications)
notification_bp.get('/nullify-action/<string:notification_id>')(NotificationService.nullifyAction)