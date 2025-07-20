from src.controllers.match_scheduler_controller import MatchSchedulerService
from src.models.match_model import MatchModel
from src.models.league_model import LeagueTeamModel
from src.utils.api_response import ApiResponse
from flask import request, jsonify
from flask.views import MethodView
from src.extensions import db

class MatchTeamsController:
    @staticmethod
    def fetch_accepted_teams_by_category(league_id: str, category_id: str):
        try:
            teams = LeagueTeamModel.query.filter_by(league_id=league_id,category_id=category_id,status="Accepted").all()

            payload = [team.to_json_for_match() for team in teams]

            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(e)
        
class MatchController(MethodView):
    def get(self, match_id=None):
        if match_id:
            match = MatchModel.query.get(match_id)
            if not match:
                return jsonify({"error": "Match not found"}), 404
            return jsonify(match.to_dict())

        matches = MatchModel.query.all()
        return jsonify([m.to_dict() for m in matches])

    def post(self):
        data = request.get_json()
        match = MatchModel(**data)
        db.session.add(match)
        db.session.commit()
        return jsonify(match.to_dict()), 201

    def put(self, match_id):
        match = MatchModel.query.get(match_id)
        if not match:
            return jsonify({"error": "Match not found"}), 404

        data = request.get_json()
        match.update(data)
        db.session.commit()
        return jsonify(match.to_dict())

    def delete(self, match_id):
        match = MatchModel.query.get(match_id)
        if not match:
            return jsonify({"error": "Match not found"}), 404

        db.session.delete(match)
        db.session.commit()
        return jsonify({"message": "Match deleted"})
    
    def get_scheduled(self, league_id, division_id=None):
        try:
            query = MatchModel.query.filter_by(status="Scheduled", league_id=league_id)
            msg = "All Scheduled"
            if division_id:
                msg = msg + " With Division"
                query = query.filter_by(division_id=division_id)

            matches = query.all()
            payload = [m.to_dict() for m in matches]
            return ApiResponse.success(payload=payload,message=msg)
        except Exception as e:
            return ApiResponse.error(e)


class MatchSchedulerController(MethodView):
    def post(self, league_id, category_id):
        try:
            data = request.get_json()
            options = data.get("options")

            if not options:
                return jsonify({"error": "Options are required"}), 400

            raw_teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=category_id,
                status="Accepted"
            ).all()

            teams = [team.to_json_for_match() for team in raw_teams]

            if not teams:
                return jsonify({"error": "No accepted teams found"}), 400

            matches = MatchSchedulerService.generateRoundRobinMatches(teams, options)

            created_matches = []
            for match_data in matches:
                match = MatchModel(**match_data)
                db.session.add(match)
                created_matches.append(match)

            db.session.commit()
            payload = [m.to_dict() for m in created_matches]
            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(e)