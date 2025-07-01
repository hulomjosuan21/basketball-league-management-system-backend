from flask import Blueprint
from src.controllers.team_controllers import TeamControllers

team_bp = Blueprint('team', __name__, url_prefix='/team')

teamControllers = TeamControllers()
team_bp.get('/<string:team_id>')(teamControllers.get_team_by_team_id)
team_bp.get('/for-league/<string:league_id>/<string:user_id>')(teamControllers.get_user_teams_for_league)
team_bp.post('/invite-player')(teamControllers.invite_player)
team_bp.post('/add-player')(teamControllers.add_player_to_team)
team_bp.put('/update-player-is_accepted')(teamControllers.update_player_team_is_accepted)
team_bp.put('/accept-invite')(teamControllers.player_team_accept_invite)
team_bp.get('/user/<string:user_id>')(teamControllers.get_teams_by_user_id)
team_bp.post('/new')(teamControllers.create_team)
team_bp.post('/<string:team_id>/players')(teamControllers.add_player)
team_bp.put('/<string:player_team_id>/captain')(teamControllers.set_team_captain)

team_bp.put('/update/<string:team_id>')(teamControllers.update_team)
team_bp.delete('/player/<string:player_team_id>/remove')(teamControllers.remove_player)