from flask import request, send_file, after_this_request
from src.services.cloudinary_service import CloudinaryService
from src.receipt_sender.send_receipt import ReceiptSender
from src.models.league_administrator_model import LeagueAdministratorModel
from src.models.league_model import LeagueModel, LeagueCategoryModel, LeaguePlayerModel, LeagueResourceModel, LeagueTeamModel
from src.models.team_model import PlayerTeamModel, TeamModel
from src.utils.api_response import ApiResponse
from src.extensions import db, docx_league_doc_template_path
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc
from rapidfuzz.fuzz import ratio
from src.utils.db_utils import AccountTypeEnum
from src.utils.file_utils import save_file
from docxtpl import DocxTemplate
from src.utils.convert import markdown_to_docx_friendly
import subprocess
import asyncio
import json
import os
import uuid
import traceback

from src.utils.model_utils import update_model_image

class LeagueResourceController:
    @staticmethod
    def create_league_resources():
        try:
            data = request.get_json()
            league_id = data.get('league_id')
            courts = data.get('league_courts', [])
            referees = data.get('league_referees', [])
            sponsors = data.get('league_sponsors', [])

            if not league_id:
                raise ValueError("league_id is required")

            existing = LeagueResourceModel.query.filter_by(league_id=league_id).first()
            if existing:
                raise ValueError("Resources already exist for this league")

            resource = LeagueResourceModel(
                league_id=league_id,
                league_courts=courts,
                league_referees=referees,
                league_sponsors=sponsors
            )

            db.session.add(resource)
            db.session.commit()

            return ApiResponse.success(
                payload=resource.to_json(),
                message="League resources created successfully."
            )

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    @staticmethod
    def update_league_resources(league_id: str):
        try:
            data = request.get_json()
            print(f"Data: {data}")
            resource = LeagueResourceModel.query.filter_by(league_id=league_id).first()

            if not resource:
                raise ValueError(f"No league resources found for league_id '{league_id}'")

            resource.copy_with(
                league_courts=data.get("league_courts"),
                league_referees=data.get("league_referees"),
                league_sponsors=data.get("league_sponsors"),
                skip_none=True,
                strict_types=False
            )

            db.session.commit()
            return ApiResponse.success(
                payload=resource.to_json(),
                message="League resources updated successfully."
            )

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    @staticmethod
    def get_league_resources(league_id: str):
        try:
            resource = LeagueResourceModel.query.filter_by(league_id=league_id).first()
            if not resource:
                raise ValueError("League resources not found")

            return ApiResponse.success(payload=resource.to_json())

        except Exception as e:
            return ApiResponse.error(str(e))

    @staticmethod
    def delete_league_resources(league_id: str):
        try:
            resource = LeagueResourceModel.query.filter_by(league_id=league_id).first()
            if not resource:
                return ApiResponse.error("League resources not found", status_code=404)

            db.session.delete(resource)
            db.session.commit()

            return ApiResponse.success(message="League resources deleted successfully.")

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
            
    @staticmethod
    def generate_league_pdf():
        try:
            BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            TEMP_DIR = os.path.join(BASE_DIR, "temp")
            os.makedirs(TEMP_DIR, exist_ok=True)

            template = DocxTemplate(docx_league_doc_template_path)

            md_description = """
                # League Details

                Welcome to the **Bogoballers League**!

                ## Requirements

                - Must be 18+
                - Must register online
                - Bring ID on game day

                1. Register
                2. Wait for approval
                3. Pay the entrance fee
            """
            context = {
                "league_title": "Josuan",
                "league_description": markdown_to_docx_friendly(md_description)
            }

            print("Final context:", context)

            file_id = uuid.uuid4().hex
            filled_docx = os.path.join(TEMP_DIR, f"{file_id}.docx")
            filled_pdf = os.path.join(TEMP_DIR, f"{file_id}.pdf")

            template.render(context)
            template.save(filled_docx)

            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", TEMP_DIR,
                filled_docx
            ], check=True)

            @after_this_request
            def cleanup(response):
                try:
                    os.remove(filled_docx)
                    os.remove(filled_pdf)
                except Exception as cleanup_err:
                    print("Cleanup failed:", cleanup_err)
                return response

            return send_file(
                filled_pdf,
                mimetype="application/pdf",
                as_attachment=False
            )

        except Exception as e:
            return ApiResponse.error(e)

class LeagueControllers:
    def filter_leagues_by_organization_details(self):
        try:
            data = request.get_json(silent=True) or {}

            org_name = data.get('organization_name', '').lower()
            brgy = data.get('barangay_name', '').lower()
            muni = data.get('municipality_name', '').lower()
            org_type = data.get('organization_type', '').lower()

            query = db.session.query(LeagueModel).join(LeagueAdministratorModel)

            if brgy:
                query = query.filter(LeagueAdministratorModel.organization_address.ilike(f"%{brgy}%"))
            if muni:
                query = query.filter(LeagueAdministratorModel.organization_address.ilike(f"%{muni}%"))

            if query.count() == 0:
                return ApiResponse.success(message="No found league",payload=[])

            if org_type:
                query = query.filter(func.lower(LeagueAdministratorModel.organization_type) == org_type)

            leagues = query.options(joinedload(LeagueModel.league_administrator)).all()

            filtered = []
            for league in leagues:
                admin = league.league_administrator
                if not admin:
                    continue

                if org_name:
                    if ratio(admin.organization_name.lower(), org_name) < 70:
                        continue

                filtered.append(league)

            payload = [l.to_json() for l in filtered]
            return ApiResponse.success(payload=payload)

        except Exception as e:
            return ApiResponse.error(str(e))
    
    async def create_league(self):
        try:
            form = request.form

            league_administrator_id = form.get('league_administrator_id')
            league_title = form.get('league_title')
            league_description = form.get('league_description')
            league_budget_str = request.form.get('league_budget')
            league_budget = float(league_budget_str)
            registration_deadline = form.get('registration_deadline')
            opening_date = form.get('opening_date')
            start_date = form.get('start_date')
            league_rules = form.get('league_rules')
            status = form.get('status')
            categories_raw = form.get('categories')

            banner_image_file = request.files.get('banner_image')
            banner_image_url = form.get('banner_image') if not banner_image_file else None

            required_fields = [
                league_administrator_id,
                league_title,
                league_description,
                registration_deadline,
                opening_date,
                start_date,
                league_rules,
                status,
                categories_raw
            ]
            if any(field is None for field in required_fields):
                return ApiResponse.error("All required fields must be provided and not null.")

            try:
                categories = json.loads(categories_raw)
            except json.JSONDecodeError:
                return ApiResponse.error("Invalid JSON format for categories.")

            if not isinstance(categories, list) or not categories:
                return ApiResponse.error("At least one category is required.")

            banner_url = None
            if banner_image_file:
                banner_url = await CloudinaryService.upload_file(banner_image_file, '/league/banners')
            elif banner_image_url:
                banner_url = banner_image_url

            league = LeagueModel(
                league_administrator_id=league_administrator_id,
                league_title=league_title,
                league_description=league_description,
                league_budget=league_budget,
                registration_deadline=datetime.fromisoformat(registration_deadline),
                opening_date=datetime.fromisoformat(opening_date),
                start_date=datetime.fromisoformat(start_date),
                league_rules=league_rules,
                status=status,
            )

            if banner_url:
                league.banner_url = banner_url

            db.session.add(league)
            db.session.flush()

            resource = LeagueResourceModel(
                league_id=league.league_id,
                league_courts=[],
                league_referees=[],
                league_sponsors=[]
            )
            db.session.add(resource)

            for cat in categories:
                category = LeagueCategoryModel(
                    league_id=league.league_id,
                    category_name=cat.get('category_name'),
                    category_format=cat.get('category_format'),
                    stage=cat.get('stage', 'Group Stage'),
                    max_team=int(cat.get('max_team', 4)),
                    entrance_fee_amount=float(cat.get('entrance_fee_amount', 0.0))
                )
                db.session.add(category)

            db.session.commit()

            return ApiResponse.success(
                message=f"New League '{league_title}' created successfully.",
                payload=league.league_id
            )

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return ApiResponse.error(f"Failed to create league: {str(e)}")
        
    async def upload_league_images(self):
        try:
            league_id = request.form.get('league_id')
            league = LeagueModel.query.get(league_id)

            if not league:
                raise ValueError("League not found")

            banner_image = request.files.get('banner_image')
            trophy_image = request.files.get('championship_trophy_image')

            tasks = []
            if banner_image:
                tasks.append(save_file(banner_image, 'banners', request))
            if trophy_image:
                tasks.append(save_file(trophy_image, 'trophies', request))

            results = await asyncio.gather(*tasks)

            i = 0
            if banner_image:
                league.banner_url = results[i]
                i += 1
            if trophy_image:
                league.championship_trophy_url = results[i]

            db.session.commit()
            return ApiResponse.success()

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

        
    def update_league(self, league_id):
        try:
            data = request.get_json()

            league = LeagueModel.query.get(league_id)
            if not league:
                return ApiResponse.error("League not found")

            if 'registration_deadline' in data:
                data['registration_deadline'] = datetime.fromisoformat(data['registration_deadline'])
            if 'opening_date' in data:
                data['opening_date'] = datetime.fromisoformat(data['opening_date'])
            if 'start_date' in data:
                data['start_date'] = datetime.fromisoformat(data['start_date'])

            league.copy_with(**{
                'league_title': data.get('league_title'),
                'league_description': data.get('league_description'),
                'league_budget': data.get('league_budget'),
                'league_rules': data.get('league_rules'),
                'status': data.get('status'),
                'sponsors': data.get('sponsors'),
                'registration_deadline': data.get('registration_deadline'),
                'opening_date': data.get('opening_date'),
                'start_date': data.get('start_date'),
            })

            db.session.commit()
            return ApiResponse.success("League updated successfully")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
    
    def delete_league(self, league_id):
        try:
            league = LeagueModel.query.get(league_id)
            if not league:
                return ApiResponse.error("League not found")

            db.session.delete(league)
            db.session.commit()
            return ApiResponse.success(message="League deleted successfully")

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    def add_player_to_league(self, player_team_id) -> LeaguePlayerModel:
        player_team = PlayerTeamModel.query.get(player_team_id)
        if not player_team:
            raise ValueError("PlayerTeam not found.")

        player_id = player_team.player_id

        existing = (
            db.session.query(LeaguePlayerModel)
            .join(PlayerTeamModel, LeaguePlayerModel.player_team_id == PlayerTeamModel.player_team_id)
            .filter(
                LeaguePlayerModel.league_id == self.league_id,
                PlayerTeamModel.player_id == player_id
            )
            .first()
        )

        if existing:
            raise ValueError("This player is already registered in this league through another team.")

        league_player = LeaguePlayerModel(
            player_team_id=player_team_id,
            league_id=self.league_id,
            league_team_id=self.league_team_id
        )
        return league_player


    async def check_players_is_allowed_or_not(self, team_id) -> list[LeaguePlayerModel]:
        try:
            team = TeamModel.query.get(team_id)

            league_players = []
            for player in team.players:
                player_team_id = player.player_team_id
                if player.is_ban or player.player.is_ban or not player.player.is_allowed:
                    raise ValueError(f"Player {player_team_id} is Banned or not Allowed to play in every league")
                else:
                    league_player = self.add_player_to_league(player_team_id)
                    league_players.append(league_player)

            return league_players
        except Exception as e:
            raise

    async def accept_team(self):
        try:
            data = request.get_json()

            league_id = data.get('league_id')
            self.league_id = league_id

            team_id = data.get('team_id')
            category_id = data.get('category_id')

            league = LeagueModel.query.get(league_id)
            self.league_administrator_id = league.league_administrator_id
            self.league_title = league.league_title

            league_admin_org_name = league.league_administrator.organization_name

            existing_league_team = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                team_id=team_id
            ).first()

            if existing_league_team:
                raise ValueError("This team is already registered in the league.")

            league_team = LeagueTeamModel(
                league_id=league_id,
                team_id=team_id,
                category_id=category_id
            )

            db.session.add(league_team)
            db.session.flush()

            self.league_team_id = league_team.league_team_id

            league_players = await self.check_players_is_allowed_or_not(team_id)
            db.session.add_all(league_players)
            db.session.commit()
            return ApiResponse.success(message=f"Wait for the {league_admin_org_name} league administrator to accept your team")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def get_league_team(self, league_team_id):
        try:
            league_team = LeagueTeamModel.query.get(league_team_id)
            if not league_team:
                raise ValueError("No Team Found!")
            
            payload = league_team.team_to_json()
            return ApiResponse.success(payload=payload)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def set_league_team_status(self, league_team_id):
        try:
            data = request.get_json()
            status = data.get('status')
            if not status:
                raise ValueError("All fields must be provided and not empty.")

            league_team = LeagueTeamModel.query.get(league_team_id)

            if not league_team:
                raise ValueError("Team not found")
            
            league_team.status = status

            db.session.commit()

            details = f"Your Team {league_team.team.team_name} has been {status}"

            return ApiResponse.success(payload=details)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def fetch_league_meta(self, league_administrator_id: str):
        try:
            league_admin = LeagueAdministratorModel.query.get(league_administrator_id)
            if not league_admin:
                return ApiResponse.error("League Administrator not found")

            active_league = league_admin.active_league

            payload = {
                "has_league": active_league is not None,
                "league_meta": active_league.to_meta_json() if active_league else None
            }

            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(str(e))

    def fetch_league_categories(self, league_id: str):
        try:
            categories = LeagueCategoryModel.query.filter_by(league_id=league_id).all()
            return ApiResponse.success(payload=[category.to_json_for_admin() for category in categories])
        except Exception as e:
            return ApiResponse.error(str(e))
    
    @staticmethod
    def update_league_banner(league_id):
        return update_model_image(
            model=LeagueModel,
            record_id=league_id,
            id_field="league_id",
            image_field="banner_url",
            folder="league/banners"
        )
        
class LeagueTeamController:
    @staticmethod
    def fetch_league_team():
        try:
            league_id = request.args.get('league_id')
            category_id = request.args.get('category_id')

            if not league_id or not category_id:
                return ApiResponse.error("Missing league_id or category_id")

            teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=category_id
            ).order_by(desc(LeagueTeamModel.created_at)).all()

            if not teams:
                return ApiResponse.success(payload=[])

            team_data = [team.to_json() for team in teams]

            return ApiResponse.success(payload=team_data)

        except Exception as e:
            return ApiResponse.error(str(e))
        
    @staticmethod
    def update_league_team(league_team_id: str):
        try:
            data = request.get_json()

            if not league_team_id:
                return ApiResponse.error("Missing league_team_id")

            league_team = LeagueTeamModel.query.get(league_team_id)

            if not league_team:
                return ApiResponse.error("League team not found")

            old_payment_status = league_team.payment_status

            updatable_fields = {k: v for k, v in data.items() if k != "league_team_id"}
            league_team.copy_with(**updatable_fields)

            db.session.commit()

            paid_statuses = ["Paid Online", "Paid On Site", "Waived"]
            if (
                league_team.payment_status in paid_statuses and 
                old_payment_status != league_team.payment_status
            ):
                receipt_sender = ReceiptSender()
                receipt_sender.send_receipt(
                    to_email="hulomjosuan@gmail.com",
                    amount=f"₱{league_team.amount_paid:,.2f}"
                )

            return ApiResponse.success()

        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return ApiResponse.error(f"Error updating league team: {str(e)}")