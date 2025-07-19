from src.models.league_model import LeagueTeamModel
from src.utils.enums import NotificationAction
from src.models.notification_model import NotificationModel
from src.utils.db_utils import AccountTypeEnum, get_new_session
from src.services.notification_serices import NotificationService
from src.models.user_model import UserModel
from src.models.player_model import PlayerModel
from src.extensions import db
from src.utils.api_response import ApiResponse
from flask import request, current_app
from src.models.team_model import TeamModel, PlayerTeamModel
from src.utils.file_utils import save_file
from sqlalchemy import or_
import difflib
from src.services.socket_service import SocketEvent, socket_service
from datetime import datetime, timezone
import threading
import eventlet

class TeamControllers:
    def get_team_by_team_id(self, team_id):
        try:
            team = TeamModel.query.filter(TeamModel.team_id == team_id).first()
            payload = team.to_json()
            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(str(e))
        
    def get_teams_by_user_id(self, user_id: str):
        try:
            teams = TeamModel.query.filter(TeamModel.user_id == user_id).all()
            if not teams:
                return ApiResponse.success(message="No teams found.", payload=[])
            
            payload = [team.to_json() for team in teams]
            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(f"Error fetching teams for user {user_id}: {str(e)}")
        
    def get_user_teams_for_league(self, league_id, user_id):
        try:
            teams = TeamModel.query.filter_by(user_id=user_id).all()

            league_teams = LeagueTeamModel.query.filter_by(league_id=league_id).all()

            league_team_map = {lt.team_id: lt.status for lt in league_teams}

            result = []

            for team in teams:
                status = league_team_map.get(team.team_id)
                already_in = status is not None

                team_data = team.to_json_for_join_league()
                team_data["already_in"] = already_in
                team_data["status"] = status

                result.append(team_data)

            return ApiResponse.success(payload=result)

        except Exception as e:
            return ApiResponse.error(str(e))

    async def create_team(self):
        try:
            user_id = request.form.get('user_id')
            team_name = request.form.get('team_name')
            team_address = request.form.get('team_address')
            contact_number = request.form.get('contact_number')
            team_motto = request.form.get('team_motto')
            coach_name = request.form.get('coach_name')
            assistant_coach_name = request.form.get('assistant_coach_name')
            
            if not all([user_id, team_name, team_address, contact_number, coach_name]):
                raise ValueError("All fields must be provided and not empty.")

            team = TeamModel(
                user_id=user_id,
                team_name=team_name,
                team_address=team_address,
                contact_number=contact_number,
                team_motto=team_motto,
                coach_name=coach_name,
                assistant_coach_name=assistant_coach_name
            )

            team_logo_image = request.files.get('team_logo_image')
            if team_logo_image:
                team_logo_url = await save_file(team_logo_image, 'team-logos', request, 'supabase')
                team.team_logo_url = team_logo_url

            db.session.add(team)
            db.session.commit()
            payload = team.to_json()
            return ApiResponse.success(message=f"New Team Created: {team_name}",payload=payload)
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def set_team_captain(self, player_team_id):
        try:
            data = request.get_json()
            team_captain_id = data.get('team_captain_id')

            if not all([player_team_id, team_captain_id]):
                raise ValueError("All fields must be provided and not empty.")

            team = TeamModel.query.get(player_team_id)
            team.team_captain_id = team_captain_id

            db.session.commit()
            return ApiResponse.success(message=f"{team_captain_id} Set as Team Captain")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    def add_player_to_team(self):
        try:
            data = request.get_json()
            team_id = data.get('team_id')
            player_id = data.get('player_id')
            is_accepted = data.get('is_accepted')

            if not all([team_id, player_id, is_accepted]):
                raise ValueError("All fields must be provided and not empty.")

            new_player_team = PlayerTeamModel(
                team_id=team_id,
                player_id=player_id,
                is_accepted=is_accepted
            )

            db.session.add(new_player_team)
            db.session.flush()
            db.session.commit()

            return ApiResponse.success(
                message=f"{new_player_team.player.last_name} has been added to the team."
            )

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
    
    def player_team_accept_invite(self):
        try:
            data = request.get_json()
            player_team_id = data.get('player_team_id')

            if not player_team_id:
                raise ValueError("Player Team ID is required.")

            player_team = PlayerTeamModel.query.filter_by(player_team_id=player_team_id).first()

            if not player_team:
                return ApiResponse.error("Player team not found.")

            player_team.is_accepted = 'Accepted'
            db.session.commit()

            user_id = player_team.player.user_id
            team_name = player_team.team.team_name
            title = "Invitation Accepted"
            body = f"You have successfully joined team '{team_name}'."

            NotificationModel.from_message(
                user_id=player_team.team.user.user_id,
                detail=f"Player accepted the invitation to join the team {team_name}.",
                author=player_team.player.full_name,
                account_type= AccountTypeEnum.TEAM_CREATOR.value,
            ).save()

            NotificationService.send_fcm(
                user_id=player_team.player.user_id,
                title=title,
                body=body
            )

            return ApiResponse.success(
                message=f"You have accepted the invitation to join team '{team_name}'."
            )

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error("An error occurred while accepting the invitation.")
            
    def update_player_team_is_accepted(self):
        try:
            data = request.get_json()
            player_team_id = data.get('player_team_id')
            is_accepted = data.get('is_accepted')

            if not all([player_team_id, is_accepted]):
                raise ValueError("Player Team ID and new is_accepted status are required.")

            player_team = PlayerTeamModel.query.get(player_team_id)
            if not player_team:
                return ApiResponse.error("Player not found in this team.")

            player_team.is_accepted = is_accepted
            db.session.commit()

            if is_accepted == "Rejected":
                message = f"You have rejected the invitation to join team '{player_team.team.team_name}'."
            elif is_accepted == "Accepted":
                message = f"You have accepted the invitation to join team '{player_team.team.team_name}'."
            else:
                message = f"Player {player_team.player.full_name}'s status updated to {is_accepted}."

            return ApiResponse.success(message=message)

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def send_player_invitation_notification(self, app, player_team_id, user_id: str, team_data, enable_fcm: bool = False):
        with app.app_context():
            try:
                payload = team_data.copy()
                payload["account_type"] = AccountTypeEnum.TEAM_CREATOR.value
                action = {
                    "type": NotificationAction.PLAYER_INVITATION.value,
                    "player_team_id": player_team_id,
                }
                payload["action"] = action
                payload["timestamp"] = datetime.now(timezone.utc).isoformat()

                notification = NotificationModel(
                    author=team_data["team_name"],
                    detail=payload["detail"],
                    image=team_data.get("team_logo_url"),
                    account_type=AccountTypeEnum.TEAM_CREATOR.value,
                    action=action,
                    team_id=team_data["team_id"],
                    team_name=team_data["team_name"],
                    team_logo_url=team_data.get("team_logo_url"),
                    user_id=user_id
                )

                db.session.add(notification)
                db.session.commit()

                payload["notification_id"] = str(notification.notification_id)

                socket_service.emit_to_user(user_id, SocketEvent.NOTIFICATION, payload)

                if enable_fcm:
                    NotificationService.send_fcm(
                        user_id, f"From: {team_data['team_name']}", payload["detail"]
                    )

            except Exception as e:
                db.session.rollback()
                print(f"[Notification Error] {e}")

    def invite_player(self):
        try:
            data = request.get_json()
            team_id = data.get('team_id')
            search = data.get('name_or_email', None)

            if not team_id or not search:
                raise ValueError("Team ID and Search (name or email) are required.")

            team = TeamModel.query.get(team_id)
            if not team:
                raise ValueError(f"Team with id {team_id} not found.")

            player = (
                db.session.query(PlayerModel)
                .join(PlayerModel.user)
                .filter(UserModel.email == search)
                .first()
            )

            if not player:
                players = db.session.query(PlayerModel.player_id, PlayerModel.full_name, PlayerModel.user_id)\
                    .filter(PlayerModel.full_name.isnot(None)).all()

                name_to_player = {p.full_name.strip(): p for p in players if p.full_name}
                best_matches = difflib.get_close_matches(
                    search.lower(),
                    [name.lower() for name in name_to_player.keys()],
                    n=1,
                    cutoff=0.5
                )

                if best_matches:
                    match = best_matches[0]
                    for full_name, p in name_to_player.items():
                        if full_name.lower() == match:
                            player = p
                            break

            if not player:
                raise ValueError("Player not found by name or email.")

            existing = PlayerTeamModel.query.filter_by(
                player_id=player.player_id,
                team_id=team_id
            ).first()

            if existing:
                return ApiResponse.error(f"{search} is already invited or in the team.", status_code=409)

            player_team = PlayerTeamModel(
                player_id=player.player_id,
                team_id=team_id,
                is_accepted='Invited'
            )
            db.session.add(player_team)
            db.session.commit()

            player_team_id = player_team.player_team_id
            user_id = player.user_id

            team_data = team.to_json_for_notification(
                f"You have been invited to join the team \"{team.team_name}\"."
            )
            team_data["team_id"] = team.team_id
            team_data["team_name"] = team.team_name
            team_data["team_logo_url"] = team.team_logo_url

            from src.server_instance import server_instance

            eventlet.spawn(lambda: self.send_player_invitation_notification(
                server_instance.server, player_team_id, user_id, team_data, True
            ))

            return ApiResponse.success(message=f"{player.full_name} invited to team.")

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    def add_player(self):
        try:
            data = request.get_json()

            team_id = data.get('team_id')
            player_id = data.get('player_id')

            if not all([team_id, player_id]):
                raise ValueError("All fields must be provided and not empty.")

            playerTeam = PlayerTeamModel(
                team_id=team_id,
                player_id=player_id
            )
        
            db.session.add(playerTeam)
            db.session.flush()
            db.session.commit()

            last_name = playerTeam.player.last_name

            return ApiResponse.success(message=f"{last_name} Player Added")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def remove_player(self, player_team_id):
        try:
            if not player_team_id:
                raise ValueError("All fields must be provided and not empty.")

            playerTeam = PlayerTeamModel.query.get(player_team_id)

            if not playerTeam:
                raise ValueError("Player not found.")

            team = playerTeam.team

            if team.team_captain_id == player_team_id:
                team.team_captain_id = None

            db.session.delete(playerTeam)
            db.session.commit()

            return ApiResponse.success(message="Player removed")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    def update_team(self, team_id):
        team = TeamModel.query.get(team_id)
        if not team:
            return ApiResponse.error("Team not found", 404)

        data = request.get_json()
        try:
            team.copy_with(**data)
            db.session.commit()
            return ApiResponse.success(message="Team updated successfully")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e), 500)
        
    def fetch_team_players(self, team_id):
        try:
            is_accepted = request.args.get('is_accepted')

            query = PlayerTeamModel.query.filter_by(team_id=team_id)

            if is_accepted:
                query = query.filter(PlayerTeamModel.is_accepted == is_accepted)

            players = query.all()

            return ApiResponse.success(
                payload=[player.to_json() for player in players]
            )
        except Exception as e:
            return ApiResponse.error(str(e), 500)