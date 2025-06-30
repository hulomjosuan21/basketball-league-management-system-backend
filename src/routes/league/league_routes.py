from flask import Blueprint

from src.controllers.league_controllers import LeagueControllers
from src.controllers.league_categories import league_categories
league_bp = Blueprint('league', __name__,url_prefix='/league')


leagueControllers = LeagueControllers()

league_bp.get('/fetch')(leagueControllers.filter_leagues_by_organization_details)
league_bp.get('/get-league-team/<string:league_team_id>')(leagueControllers.get_league_team)
league_bp.get('/category-list')(league_categories)

league_bp.post('/create-new')(leagueControllers.create_league)

league_bp.put('/upload/images')(leagueControllers.upload_league_images)
league_bp.put('/modify/<string:league_id>')(leagueControllers.update_league)

league_bp.delete('/delete/<string:league_id>')(leagueControllers.delete_league)

league_bp.patch('/accept-team')(leagueControllers.accept_team)
league_bp.patch('/league-team/set-status/<string:league_team_id>')(leagueControllers.set_league_team_status)