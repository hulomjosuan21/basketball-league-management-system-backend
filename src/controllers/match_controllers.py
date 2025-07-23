from src.controllers.match_scheduler_controller import MatchSchedulerService
from src.models.match_model import MatchModel
from src.models.league_model import LeagueTeamModel
from src.utils.api_response import ApiResponse
from flask import request, jsonify
from flask.views import MethodView
from src.extensions import db
from datetime import datetime

class MatchController():
    @staticmethod
    def has_existing_matches():
        try:
            data = request.get_json()
            options = data

            league_id = options.get("league_id")
            category = options.get("category")
            division_id = options.get("division_id")

            if not all([league_id, category, division_id]):
                return ApiResponse.error("Missing required parameters"), 400

            total = MatchModel.query.filter_by(
                league_id=league_id,
                category=category,
                division_id=division_id
            ).count()

            return ApiResponse.success(payload={"exists": total > 0, "total": total})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.error(str(e)), 500
        
    def rematch_versus_teams(self):
        try:
            data = request.get_json()
            options = data.get("options")

            league_id = options.get("league_id")
            division_id = options.get("division_id")
            category = options.get("category")

            if not all([league_id, division_id, category]):
                return ApiResponse.error("Missing required parameters."), 400

            MatchModel.query.filter_by(
                league_id=league_id,
                division_id=division_id,
                category=category
            ).delete()

            db.session.commit()

            raw_teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=division_id,
                status="Accepted"
            ).all()

            teams = [team.to_json_for_match() for team in raw_teams]

            if not teams:
                return ApiResponse.error("No accepted teams found."), 400

            matches = MatchSchedulerService.generateRoundRobinMatches(teams, options)

            created_matches = []
            for match_data in matches:
                match = MatchModel(**match_data)
                db.session.add(match)
                created_matches.append(match)

            db.session.commit()
            total = len(created_matches)

            return ApiResponse.success(
                message=f"{total} matchups successfully regenerated.",
                payload={"exists": total > 0, "total": total}
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.error(str(e)), 500
        
    def schedule_match(self):
        data = request.get_json()

        match_id = data.get("match_id")
        if not match_id:
            return jsonify({"error": "Missing match_id"}), 400

        match: MatchModel = MatchModel.query.get(match_id)
        if not match:
            return jsonify({"error": "Match not found"}), 404

        try:
            update_data = {
                "scheduled_date": datetime.fromisoformat(data["scheduled_date"].replace("Z", "+00:00")) if data.get("scheduled_date") else None,
                "referees": data.get("referees", []),
                "court": data.get("court"),
                "match_notes": data.get("match_notes"),
                "duration_minutes": data.get("duration_minutes"),
                "status": "Scheduled"
            }

            match.copy_with(skip_none=True, **update_data)
            db.session.commit()

            return ApiResponse.success(
                message=f"Match scheduled successfully",
                payload=match.to_dict()
            )            
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e)), 500

    def generate_versus_teams(self):
        try:
            data = request.get_json()
            options = data.get("options")

            league_id = options.get('league_id')
            division_id = options.get('division_id')

            if not options:
                return jsonify({"error": "Options are required"}), 400

            raw_teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=division_id,
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
            total = len(created_matches)
            return ApiResponse.success(
                message=f"{total} matchups successfully generated." if total else "No matchups were generated.",
                payload={"exists": total > 0, "total": total}
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.error(e)

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
    
    def get_all_matches(self):
        try:
            data = request.get_json()
            options = data

            league_id = options.get('league_id')
            division_id = options.get('division_id', None)
            status = options.get('status')

            query = MatchModel.query.filter_by(status=status, league_id=league_id)
            msg = "All Scheduled"
            if division_id:
                msg = msg + " With Division"
                query = query.filter_by(division_id=division_id)

            matches = query.all()
            payload = [m.to_dict() for m in matches]
            return ApiResponse.success(payload=payload,message=msg)
        except Exception as e:
            return ApiResponse.error(e)