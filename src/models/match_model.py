from src.models.team_model import TeamModel
from src.extensions import db, ph
from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from src.utils.db_utils import AccountTypeEnum, CreatedAt, UUIDGenerator, UpdatedAt, create_account_type_enum
import re

class MatchModel(db.Model):
    __tablename__ = "matches_table"

    # 🔑 Core Identification
    match_id = UUIDGenerator(db, "match")
    league_id = db.Column(db.String, db.ForeignKey("leagues.league_id"), nullable=True)
    division = db.Column(db.String(100), nullable=True)

    # 👥 Teams
    home_team_id = db.Column(db.String, db.ForeignKey("teams.team_id"), nullable=False)
    away_team_id = db.Column(db.String, db.ForeignKey("teams.team_id"), nullable=False)

    home_team_score = db.Column(db.String, nullable=True)
    away_team_score = db.Column(db.String, nullable=True)

    winner_team_id = db.Column(db.String, db.ForeignKey("teams.team_id"), nullable=True)
    loser_team_id = db.Column(db.String, db.ForeignKey("teams.team_id"), nullable=True)

    # 📅 Schedule
    scheduled_date = db.Column(db.DateTime(timezone=True), nullable=False)
    duration_minutes = db.Column(db.String, nullable=False)
    court = db.Column(db.String(100), nullable=False)
    referees = db.Column(JSONB, nullable=True)

    # 🧾 Details
    category = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="scheduled")
    match_notes = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)

    # 🧭 Bracket Navigation
    round_number = db.Column(db.String, nullable=True)
    bracket_side = db.Column(db.String(20), nullable=False)
    bracket_position = db.Column(db.String(50), nullable=True)

    previous_match_ids = db.Column(JSONB, default=list)
    next_match_id = db.Column(db.String, db.ForeignKey("matches.match_id"), nullable=True)
    next_match_slot = db.Column(db.String(20), nullable=False)

    loser_next_match_id = db.Column(db.String, db.ForeignKey("matches.match_id"), nullable=True)
    loser_next_match_slot = db.Column(db.String(20), nullable=True)

    # 🛠️ Generation
    pairing_method = db.Column(db.String(50), nullable=False)
    generated_by = db.Column(db.String(100), nullable=True)

    # 🎯 UI Helpers
    display_name = db.Column(db.String(100), nullable=True)
    is_final = db.Column(db.Boolean, default=False)
    is_third_place = db.Column(db.Boolean, default=False)

    # 📆 Audit
    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    # 🔁 Relationships (no reverse)
    @property
    def home_team(self):
        return db.session.get(TeamModel, self.home_team_id)

    @property
    def away_team(self):
        return db.session.get(TeamModel, self.away_team_id)

    @property
    def winner_team(self):
        return db.session.get(TeamModel, self.winner_team_id) if self.winner_team_id else None

    @property
    def loser_team(self):
        return db.session.get(TeamModel, self.loser_team_id) if self.loser_team_id else None

    next_match = db.relationship("MatchModel", remote_side=[match_id], foreign_keys=[next_match_id], post_update=True)
    loser_next_match = db.relationship("MatchModel", remote_side=[match_id], foreign_keys=[loser_next_match_id], post_update=True)