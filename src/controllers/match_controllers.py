from src.models.league_model import LeagueTeamModel
from src.utils.api_response import ApiResponse

class MatchTeamsController:
    @staticmethod
    def fetch_accepted_teams_by_category(league_id: str, category_id: str):
        try:
            teams = LeagueTeamModel.query.filter_by(league_id=league_id,category_id=category_id,status="Accepted").all()

            payload = [team.to_json_for_match() for team in teams]

            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(e)