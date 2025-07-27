from src.controllers.match_scheduler_controller import MatchSchedulerService
from src.models.match_model import MatchModel, MatchStageModel
from src.models.league_model import LeagueTeamModel
from src.utils.api_response import ApiResponse
from flask import request, jsonify
from flask.views import MethodView
from src.extensions import db
from datetime import datetime

class MatchStageController:
    def get_match_stages(self,league_id, division_id):
        try:
            if not league_id or not division_id:
                return ApiResponse.error("league_id and division_id are required")

            stages = MatchStageModel.query.filter_by(
                league_id=league_id,
                division_id=division_id
            ).order_by(MatchStageModel.created_at.desc()).all()

            return ApiResponse.success(
                payload=[s.to_dict() for s in stages]
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.error(e)

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

    def rematch_versus_teams(self):
        try:
            data = request.get_json()
            options = data.get("options")
            stage_id = data.get("stage_id")

            if not stage_id:
                raise ValueError("stage_id is required.")

            stage = MatchStageModel.query.get(stage_id)
            if not stage:
                raise ValueError("Stage not found.")

            league_id = stage.league_id
            division_id = stage.division_id
            category = stage.category

            if not options:
                raise ValueError("Match options are required.")

            format_type = options.get("format_type", "Round Robin")

            if stage.format_type != format_type:
                stage.format_type = format_type

            if stage.match_options != options:
                stage.match_options = options

            MatchModel.query.filter_by(
                league_id=league_id,
                division_id=division_id,
                category=category,
                stage_id=stage_id
            ).delete()

            db.session.commit()

            raw_teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=division_id,
                status="Accepted"
            ).all()

            teams = [team.to_json_for_match() for team in raw_teams]
            if not teams:
                raise ValueError("No accepted teams found.")

            if format_type == "Knockout":
                matches = MatchSchedulerService.generateKnockoutMatches(teams, options)
            elif format_type == "Double Elimination":
                matches = MatchSchedulerService.generateDoubleEliminationMatches(teams, options)
            else:
                matches = MatchSchedulerService.generateRoundRobinMatches(teams, options)

            created_matches = []
            for match_data in matches:
                match_data["stage_id"] = stage_id
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
            return ApiResponse.error("An unexpected error occurred."), 500

    def generate_versus_teams(self):
        try:
            data = request.get_json()
            options = data.get("options")
            format_type = options.get("format_type", "Round Robin")

            if not options:
                raise ValueError("Missing options for match generation.")

            league_id = options.get("league_id")
            division_id = options.get("division_id")

            if not league_id or not division_id:
                raise ValueError("Missing required parameters: league_id or division_id")

            raw_teams = LeagueTeamModel.query.filter_by(
                league_id=league_id,
                category_id=division_id,
                status="Accepted"
            ).all()

            teams = [team.to_json_for_match() for team in raw_teams]

            if not teams:
                raise ValueError("No accepted teams found for the specified league and division.")

            new_stage = MatchStageModel(
                league_id=league_id,
                division_id=division_id,
                category=options.get("category", "Elimination"),
                pairing_method=options.get("pairing_method", "random"),
                auto_generate=True,
                vs_teams_generated=False,
                match_options=options,
                created_by=options.get("generated_by"),
                format_type=format_type
            )
            db.session.add(new_stage)
            db.session.flush()

            if format_type == "Knockout":
                matches_data = MatchSchedulerService.generateKnockoutMatches(teams, options)
            elif format_type == "Double Elimination":
                matches_data = MatchSchedulerService.generateDoubleEliminationMatches(teams, options)
            else:
                matches_data = MatchSchedulerService.generateRoundRobinMatches(teams, options)

            created_matches = []
            for match_data in matches_data:
                match = MatchModel(**match_data)
                match.stage_id = new_stage.stage_id
                db.session.add(match)
                created_matches.append(match)

            new_stage.vs_teams_generated = True

            db.session.commit()

            total = len(created_matches)
            return ApiResponse.success(
                message=f"{total} matchups successfully generated.",
                payload={
                    "exists": total > 0,
                    "total": total,
                    "stage_id": new_stage.stage_id
                }
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.error(e)
    
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