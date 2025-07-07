from flask import Blueprint
from src.controllers.player_controllers import PlayerControllers
player_bp = Blueprint('player', __name__, url_prefix='/player')

player_controllers = PlayerControllers()

player_bp.put('/update/<string:by>/<string:player_id>')(player_controllers.update_player)

