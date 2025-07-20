from src.controllers.match_controllers import MatchController, MatchSchedulerController, MatchTeamsController
from flask import Blueprint

match_bp = Blueprint("match", __name__, url_prefix="/match")

match_bp.get('/teams/<string:league_id>/<string:category_id>')(MatchTeamsController.fetch_accepted_teams_by_category)

match_view = MatchController.as_view("match")
scheduler_view = MatchSchedulerController.as_view("match_scheduler")

match_bp.add_url_rule("/games", view_func=match_view, methods=["GET", "POST"])
match_bp.add_url_rule("/games/<string:match_id>", view_func=match_view, methods=["GET", "PUT", "DELETE"])

match_bp.add_url_rule(
    "/schedule/<string:league_id>/<string:category_id>",
    view_func=scheduler_view,
    methods=["POST"]
)

match_bp.add_url_rule(
    "/all/scheduled/<string:league_id>",
    view_func=MatchController().get_scheduled,
    methods=["GET"],
    endpoint="get_scheduled_by_league"
)

match_bp.add_url_rule(
    "/all/scheduled/<string:league_id>/<string:division_id>",
    view_func=MatchController().get_scheduled,
    methods=["GET"],
    endpoint="get_scheduled_by_league_and_division"
)