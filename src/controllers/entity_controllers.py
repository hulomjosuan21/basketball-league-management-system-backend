from datetime import timedelta
from flask_jwt_extended import create_access_token
from src.models.league_administrator_model import LeagueAdministratorModel
from src.services.email_services import send_verification_email
from src.errors.errors import AuthException
from src.utils.file_utils import save_file
from src.models.player_model import PlayerModel
from src.utils.api_response import ApiResponse
from src.extensions import db
from flask import request
from src.models.user_model import UserModel
from src.utils.db_utils import AccountTypeEnum
from flask_jwt_extended import set_access_cookies
from flask_cors import cross_origin

class EntityControllers:
    async def create_team_creator(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password_str = data.get('password_str')
            account_type = data.get('account_type')
            contact_number = data.get('contact_number')

            if not all([email, password_str, account_type, contact_number]):
                raise ValueError("All fields must be provided and not empty.")
            user = UserModel(
                email=email,
                contact_number=contact_number,
                account_type=account_type
            )
            user.set_password(password_str)

            db.session.add(user)
            db.session.commit()
            
            verify_link = f"/user/{user.user_id}"

            await send_verification_email(email, verify_link, request)

            message = "A verification link has been sent to your email. Please verify your account before logging in."
            
            return ApiResponse.success(redirect="/client/login",message=message,status_code=201)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(e)
        
    async def create_player(self):
        try:
            email = request.form.get('user[email]')
            password_str = request.form.get('user[password_str]')
            account_type = request.form.get('user[account_type]')
            contact_number = request.form.get('user[contact_number]')

            if not all([email, password_str, account_type, contact_number]):
                raise ValueError("All fields must be provided and not empty.")
            user = UserModel(
                email=email,
                contact_number=contact_number,
                account_type=account_type
            )
            user.set_password(password_str)

            full_name = request.form.get('full_name')
            gender = request.form.get('gender')
            birth_date = request.form.get('birth_date')

            player_address = request.form.get('player_address')

            jersey_name = request.form.get('jersey_name')
            jersey_number = request.form.get('jersey_number')
            position = request.form.get('position')

            height_in = request.form.get('height_in')
            weight_kg = request.form.get('weight_kg')

            profile_image = request.files.get('profile_image')

            if not all([full_name, gender, birth_date, jersey_name, jersey_number, position, profile_image, player_address]):
                raise ValueError("All fields must be provided and not empty.")

            profile_image_url = await save_file(profile_image, 'profiles', request, 'supabase')
            player = PlayerModel(
                full_name=full_name,
                gender=gender,
                birth_date=birth_date,
                player_address=player_address,
                jersey_name=jersey_name,
                jersey_number=jersey_number,
                position=position,
                height_in=float(height_in) if height_in else None,
                weight_kg=float(weight_kg) if weight_kg else None,
                profile_image_url=profile_image_url,
                user=user
            )
            db.session.add(user)
            db.session.add(player)
            db.session.commit()

            verify_link = f"/user/{user.user_id}"

            await send_verification_email(email, verify_link, request)

            message = "A verification link has been sent to your email. Please verify your account before logging in."
            
            return ApiResponse.success(redirect="/client/login/screen",message=message,status_code=201)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(e)
        
    async def create_league_administrator(self):
        try:
            email = request.form.get('user[email]')
            password_str = request.form.get('user[password_str]')
            account_type = request.form.get('user[account_type]')
            contact_number = request.form.get('user[contact_number]')

            organization_type = request.form.get('organization_type')
            organization_name = request.form.get('organization_name')
            organization_address = request.form.get('organization_address')

            organization_logo = request.files.get('organization_logo')

            if not all([email, password_str, account_type, organization_name, contact_number, organization_address]):
                raise ValueError("All fields must be provided and not empty.")
            
            user = UserModel(
                email=email,
                contact_number=contact_number,
                account_type=account_type
            )
            user.set_password(password_str)

            league_administrator = LeagueAdministratorModel(
                user=user,
                organization_type=organization_type,
                organization_name=organization_name,
                organization_address=organization_address,
            )
            
            full_url = await save_file(organization_logo, 'images', request, 'supabase')
            league_administrator.organization_logo_url = full_url

            db.session.add(user)
            db.session.add(league_administrator)
            db.session.commit()

            verify_link = f"/user/{user.user_id}"

            await send_verification_email(email, verify_link, request)

            message = "A verification link has been sent to your email. Please verify your account before logging in."

            return ApiResponse.success(redirect="/administrator/login/sreen", message=message,status_code=201)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(e)
        
    def login_entity(self):
        try:
            stay_login = str(request.args.get('stay_login', 'true')).lower() == 'true'
            email = request.form.get('email')
            password_str = request.form.get('password_str')

            if not email or not password_str:
                raise ValueError("Missing required fields: email, password")

            user = UserModel.query.filter(UserModel.email == email).first()

            if not user or not user.verify_password(password_str):
                raise AuthException("Invalid email or password.", 401)

            if not user.is_verified:
                raise AuthException("Your account is not verified.", 403)
            
            account_type = str(user.account_type)

            match account_type:
                case AccountTypeEnum.PLAYER.value:
                    entity = PlayerModel.query.filter_by(user_id=user.user_id).first()
                    redirect = '/player/home/screen'
                case AccountTypeEnum.TEAM_CREATOR.value:
                    entity = user
                    redirect = '/team-creator/home/screen'
                case AccountTypeEnum.LOCAL_ADMINISTRATOR.value | AccountTypeEnum.LGU_ADMINISTRATOR.value:
                    entity = LeagueAdministratorModel.query.filter_by(user_id=user.user_id).first()
                    redirect = '/administrator/main/screen'
                case _:
                    raise ValueError(f"Unknown account type {account_type}")

            additional_claims = {
                "account_type": str(account_type)
            }

            access_token = None
            if stay_login:
                access_token = create_access_token(
                    identity=user.user_id,
                    additional_claims=additional_claims,
                    expires_delta=timedelta(weeks=1)
                )

            payload = {
                'access_token': access_token,
                'entity': entity.to_json(),
                'account_type': account_type,
                'user_id': user.user_id
            }

            response = ApiResponse.success(
                redirect=redirect,
                message="Login successful.",
                payload=payload
            )

            if stay_login and access_token:
                set_access_cookies(response, access_token)

            return response
        except Exception as e:
            return ApiResponse.error(e)
    
    @cross_origin(origins=["http://localhost:3000"], supports_credentials=True)
    def admin_login(self):
        try:
            stay_login = str(request.args.get('stay_login', 'true')).lower() == 'true'
            email = request.form.get('email')
            password_str = request.form.get('password_str')

            if not email or not password_str:
                raise ValueError("Missing required fields: email, password")

            user = UserModel.query.filter(UserModel.email == email).first()

            if not user or not user.verify_password(password_str):
                raise AuthException("Invalid email or password.", 401)

            if not user.is_verified:
                raise AuthException("Your account is not verified.", 403)
            
            account_type = str(user.account_type)
            match account_type:
                case AccountTypeEnum.LOCAL_ADMINISTRATOR.value | AccountTypeEnum.LGU_ADMINISTRATOR.value:
                    entity = LeagueAdministratorModel.query.filter_by(user_id=user.user_id).first()
                    redirect = '/league-administrator/pages/dashboard'
                case _:
                    raise ValueError(f"Unknown account type {account_type}")         
                
            additional_claims = {
                "account_type": str(account_type),
                "league_administrator_id": entity.league_administrator_id
            }

            access_token = None
            if stay_login:
                access_token = create_access_token(
                    identity=user.user_id,
                    additional_claims=additional_claims,
                    expires_delta=timedelta(weeks=1)
                )

            payload = {
                'access_token': access_token,
                'entity': entity.to_json(),
                'account_type': account_type,
                'user_id': user.user_id
            }

            response = ApiResponse.success(
                redirect=redirect,
                message="Login successful.",
                payload=payload
            )

            if stay_login and access_token:
                set_access_cookies(response, access_token)

            return response
        except Exception as e:
            return ApiResponse.error(e)       
        
    def fetch_entity(self, user_id):
        try:
            if not user_id:
                raise ValueError("Missing user id.")
            
            user = UserModel.query.get(user_id)

            account_type = str(user.account_type)

            match account_type:
                case AccountTypeEnum.PLAYER.value:
                    entity = PlayerModel.query.filter_by(user_id=user.user_id).first()
                case AccountTypeEnum.TEAM_CREATOR.value:
                    entity = user
                case AccountTypeEnum.LOCAL_ADMINISTRATOR.value | AccountTypeEnum.LGU_ADMINISTRATOR.value:
                    entity = LeagueAdministratorModel.query.filter_by(user_id=user.user_id).first()
                case _:
                    raise ValueError(f"Unknown account type {account_type}")
                
            payload = {
                'entity': entity.to_json(),
                'account_type': account_type
            }
                
            return ApiResponse.success(message="Fetch successful.",payload=payload)
        except Exception as e:
            return ApiResponse.error(e)