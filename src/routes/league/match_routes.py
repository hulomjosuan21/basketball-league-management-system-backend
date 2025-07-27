from src.controllers.match_controllers import MatchController, MatchStageController
from flask import Blueprint

match_bp = Blueprint("match", __name__, url_prefix="/match")

match_controller = MatchController()
matchStageController = MatchStageController()

match_bp.post('/check-exists')(MatchController.has_existing_matches)
match_bp.post('/generate')(match_controller.generate_versus_teams)
match_bp.patch("/rematch")(match_controller.rematch_versus_teams)
match_bp.get('/all/<string:league_id>/<string:division_id>')(matchStageController.get_match_stages)
match_bp.put('/schedule')(match_controller.schedule_match)