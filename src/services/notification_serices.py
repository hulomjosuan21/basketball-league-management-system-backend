from firebase_admin import messaging
from src.models.notification_model import NotificationModel
from src.models.user_model import UserModel
from src.utils.api_response import ApiResponse
from src.extensions import db

class NotificationService:
    @staticmethod
    def send_fcm(user_id: str, title: str, body: str) -> ApiResponse:
        try:
            user = UserModel.query.get(user_id)
            if not user or not user.fcm_token:
                return ApiResponse.error("User or FCM token not found")

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=user.fcm_token,
            )
            messaging.send(message)
            print(f"[FCM] Sent push to {user_id}")
            return ApiResponse.success()
        except Exception as e:
            print(f"[FCM] Error sending to {user_id}: {e}")
            return ApiResponse.error(str(e))

    @staticmethod
    def fetchNotifications(user_id: str):
        try:
            notifications = (
                NotificationModel.query
                .filter_by(user_id=user_id)
                .order_by(NotificationModel.timestamp.desc())
                .all()
            )

            if not notifications:
                return ApiResponse.success(payload=[])
            
            notifications_json = [notification.to_json() for notification in notifications]
            return ApiResponse.success(payload=notifications_json)
        except Exception as e:
            return ApiResponse.error(str(e))
        
    @staticmethod
    def nullifyAction(notification_id: str):
        try:
            notification = NotificationModel.query.get(notification_id)

            notification.action = None

            db.session.commit()
            return ApiResponse.success('Action nullified successfully.')
        except Exception as e:
            return ApiResponse.error(str(e))
        