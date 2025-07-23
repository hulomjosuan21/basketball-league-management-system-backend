from src.controllers.match_controllers import MatchController
from flask import Blueprint

match_bp = Blueprint("match", __name__, url_prefix="/match")

match_controller = MatchController()

match_bp.post('/check-exists')(MatchController.has_existing_matches)
match_bp.post('/generate')(match_controller.generate_versus_teams)
match_bp.post("/rematch")(match_controller.rematch_versus_teams)
match_bp.post('/all')(match_controller.get_all_matches)
match_bp.put('/schedule')(match_controller.schedule_match)