from src.models.league_model import LeagueTeamModel
from src.extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from src.utils.db_utils import CreatedAt, UUIDGenerator, UpdatedAt

class MatchModel(db.Model):
    __tablename__ = "matches_table"

    match_id = UUIDGenerator(db,"match")

    league_id = db.Column(db.String, nullable=False)
    division_id = db.Column(db.String, nullable=True)

    home_team_id = db.Column(db.String, nullable=False)
    away_team_id = db.Column(db.String, nullable=False)

    @property
    def home_team(self) -> dict:
        team = LeagueTeamModel.query.get(self.home_team_id)
        return team.to_json_for_match()

    @property
    def away_team(self) -> dict:
        team = LeagueTeamModel.query.get(self.away_team_id)
        return team.to_json_for_match()

    home_team_score = db.Column(db.Integer, nullable=True)
    away_team_score = db.Column(db.Integer, nullable=True)

    winner_team_id = db.Column(db.String, nullable=True)
    loser_team_id = db.Column(db.String, nullable=True)

    scheduled_date = db.Column(db.DateTime(timezone=True), nullable=True)
    duration_minutes = db.Column(db.Integer, default=40)

    court = db.Column(db.String, nullable=True)
    referees = db.Column(db.ARRAY(db.String), default=[])

    category = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default="Scheduled")

    match_notes = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)

    round_number = db.Column(db.Integer, nullable=True)
    bracket_side = db.Column(db.String, nullable=True)
    bracket_position = db.Column(db.String, nullable=True)

    previous_match_ids = db.Column(db.ARRAY(db.String), default=[])
    next_match_id = db.Column(db.String, nullable=True)
    next_match_slot = db.Column(db.String, nullable=True)  # home_team/away_team

    loser_next_match_id = db.Column(db.String, nullable=True)
    loser_next_match_slot = db.Column(db.String, nullable=True)

    pairing_method = db.Column(db.String, nullable=True)  # manual/random/seeded
    generated_by = db.Column(db.String, nullable=True)
    display_name = db.Column(db.String, nullable=True)

    is_final = db.Column(db.Boolean, default=False)
    is_third_place = db.Column(db.Boolean, default=False)

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "league_id": self.league_id,
            "division_id": self.division_id,
            "home_team_id": self.home_team_id,
            "away_team_id": self.away_team_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_team_score": self.home_team_score,
            "away_team_score": self.away_team_score,
            "winner_team_id": self.winner_team_id,
            "loser_team_id": self.loser_team_id,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "duration_minutes": self.duration_minutes,
            "court": self.court,
            "referees": self.referees,
            "category": self.category,
            "status": self.status,
            "match_notes": self.match_notes,
            "is_featured": self.is_featured,
            "round_number": self.round_number,
            "bracket_side": self.bracket_side,
            "bracket_position": self.bracket_position,
            "previous_match_ids": self.previous_match_ids,
            "next_match_id": self.next_match_id,
            "next_match_slot": self.next_match_slot,
            "loser_next_match_id": self.loser_next_match_id,
            "loser_next_match_slot": self.loser_next_match_slot,
            "pairing_method": self.pairing_method,
            "generated_by": self.generated_by,
            "display_name": self.display_name,
            "is_final": self.is_final,
            "is_third_place": self.is_third_place,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
