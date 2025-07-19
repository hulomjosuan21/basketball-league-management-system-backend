from src.controllers.match_controllers import MatchTeamsController
from flask import Blueprint

match_bp = Blueprint('match', __name__,url_prefix='/match')

match_bp.get('/teams/<string:league_id>/<string:category_id>')(MatchTeamsController.fetch_accepted_teams_by_category)