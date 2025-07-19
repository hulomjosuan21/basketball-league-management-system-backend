from flask import Blueprint

from src.controllers.league_controllers import LeagueControllers, LeagueResourceController, LeagueTeamController
from src.controllers.league_categories import league_categories
league_bp = Blueprint('league', __name__,url_prefix='/league')


leagueControllers = LeagueControllers()

league_bp.get('/fetch')(leagueControllers.filter_leagues_by_organization_details)
league_bp.get('/get-league-team/<string:league_team_id>')(leagueControllers.get_league_team)
league_bp.get('/meta/<string:league_administrator_id>')(leagueControllers.fetch_league_meta)
league_bp.get('/category-list')(league_categories)

league_bp.post('/create-new')(leagueControllers.create_league)

league_bp.put('/upload/images')(leagueControllers.upload_league_images)
league_bp.put('/modify/<string:league_id>')(leagueControllers.update_league)

league_bp.delete('/delete/<string:league_id>')(leagueControllers.delete_league)

league_bp.patch('/accept-team')(leagueControllers.accept_team)
league_bp.patch('/league-team/set-status/<string:league_team_id>')(leagueControllers.set_league_team_status)
league_bp.patch('/update/banner/<league_id>')(LeagueControllers.update_league_banner)

league_bp.get('/resource/<string:league_id>')(LeagueResourceController.get_league_resources)
league_bp.post('/resource/create')(LeagueResourceController.create_league_resources)
league_bp.put('/resource/update/<string:league_id>')(LeagueResourceController.update_league_resources)
league_bp.delete('/resource/delete/<string:league_id>')(LeagueResourceController.delete_league_resources)

league_bp.get('/league-team')(LeagueTeamController.fetch_league_team)
league_bp.put('/league-team/update/<string:league_team_id>')(LeagueTeamController.update_league_team)

league_bp.get('/generate-pdf')(LeagueResourceController.generate_league_pdf)
league_bp.get('/current/categories/<string:league_id>')(leagueControllers.fetch_league_categories)