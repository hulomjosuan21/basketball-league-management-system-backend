from flask import Blueprint

from src.controllers.entity_controllers import EntityControllers

entity_bp = Blueprint('entity', __name__, url_prefix='/entity')

entityControllers = EntityControllers()

entity_bp.get('/fetch/<string:user_id>')(entityControllers.fetch_entity)

entity_bp.post('/create-new/player')(entityControllers.create_player)
entity_bp.post('/create-new/team-creator')(entityControllers.create_team_creator)
entity_bp.post('/create-new/league-administrator')(entityControllers.create_league_administrator)
entity_bp.post('login')(entityControllers.login_entity)