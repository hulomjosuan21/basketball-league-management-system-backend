from src.models.user_model import UserModel
from flask import request
from src.utils.api_response import ApiResponse
from src.utils.html_template import email_html_template
from src.extensions import db

class UserControllers:
    def verify_administrator_account(self, user_id):
        try:
            if not user_id:
                raise ValueError("Missing user credentials")

            user = UserModel.query.filter_by(user_id=user_id).first()

            if not user:
                return ApiResponse.html(
                    template=email_html_template("Verification Failed", "User not found.",'error'), status_code=404
                )

            if user.is_verified:
                return ApiResponse.html(
                    template=email_html_template("Already Verified", "Your account is already verified.",'info'), status_code=200
                )
            
            user.is_verified = True
            db.session.commit()
            return ApiResponse.html(
                template=email_html_template("Account Verified", "Your account has been verified successfully!",'info'), status_code=200
            )
         
        except Exception as e:
            return ApiResponse.html(
                template=email_html_template("Error Occurred","✕ Something went wrong!",'error'), status_code=500
            )
        
    def set_fcm_token(self, user_id):
        try:
            data = request.get_json()
            token = data.get('token', None)
            if not user_id:
                raise ValueError("Missing user credentials")
            
            user = UserModel.query.get(user_id)

            user.fcm_token = token

            db.session.commit()

            return ApiResponse.success(message="Supabase initialized successfully!")
        except Exception as e:
            return ApiResponse.error(str(e))