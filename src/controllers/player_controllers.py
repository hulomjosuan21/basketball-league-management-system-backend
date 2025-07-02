from src.models.player_model import PlayerModel
from src.extensions import db
from src.utils.api_response import ApiResponse
from flask import request

class PlayerControllers:
    async def update_player(self,by,player_id):
        player = PlayerModel.query.get(player_id)
        if not player:
            return ApiResponse.error("Player not found", 404)
        try:
            if by == 'profile':
                data = request.get_json()
                player.copy_with(**data)
                db.session.commit()
            return ApiResponse.success(message="Updated successfully")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e), 500)