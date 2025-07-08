from src.models.images_model import Image
from src.utils.db_utils import CreatedAt, UUIDGenerator, UpdatedAt
from src.extensions import db
from datetime import datetime
from copy import deepcopy
from sqlalchemy.dialects.postgresql import JSONB
from src.utils.mixins import UpdatableMixin

class LeagueResourceModel(db.Model, UpdatableMixin):
    __tablename__ = 'league_resource_table'
    league_resource_id = UUIDGenerator(db, 'league_resource')

    league_id = db.Column(
        db.String,
        db.ForeignKey('leagues_table.league_id', ondelete='CASCADE'),
        nullable=False
    )

    league_courts = db.Column(JSONB, nullable=True)
    league_referees = db.Column(JSONB, nullable=True)

    def to_json(self):
        return {
            "league_resource_id": self.league_resource_id,
            "league_id": self.league_id,
            "league_courts": self.league_courts or [],
            "league_referees": self.league_referees or [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

class LeagueModel(db.Model):
    __tablename__ = 'leagues_table'

    league_id = UUIDGenerator(db, 'league')
    league_administrator_id = db.Column(
        db.String, 
        db.ForeignKey('league_administrator_table.league_administrator_id', ondelete="CASCADE"),
        nullable=False
    )

    league_title = db.Column(db.String(100), nullable=False)
    league_description = db.Column(db.Text, nullable=False)
    league_budget = db.Column(db.Float, nullable=False, default=0.0)

    registration_deadline = db.Column(db.DateTime, nullable=False)
    opening_date = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)

    banner_url = db.Column(db.String, nullable=True)

    @property
    def championship_trophy_images(self):
        return Image.query.filter_by(
            entity_id=self.league_id,
            tag='trophy'
        ).all() or []
    
    status = db.Column(db.Enum('Scheduled', 'Ongoing', 'Completed', 'Postponed', 'Cancelled', name="league_status"), nullable=False, default="Scheduled")

    season_year = db.Column(db.Integer, nullable=False, default=datetime.now().year)
    league_rules = db.Column(db.Text, nullable=False)
    
    sponsors = db.Column(db.Text, nullable=True)

    # many to one
    league_administrator = db.relationship(
        'LeagueAdministratorModel',
        back_populates='created_leagues',
        passive_deletes=True
    )

    categories = db.relationship(
        'LeagueCategoryModel',
        back_populates='league',
        cascade='all, delete-orphan'
    )

    league_teams = db.relationship(
        'LeagueTeamModel',
        back_populates='league',
        cascade='all, delete-orphan'
    )

    payments = db.relationship('PaymentModel', back_populates='league', cascade="all, delete-orphan")


    def copy_with(self, *, skip_none=True, strict_types=False, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"[LeagueModel] No attribute named '{key}'")

            # Skip None values if requested
            if skip_none and value is None:
                continue

            current_value = getattr(self, key)

            if strict_types and value is not None and current_value is not None:
                if not isinstance(value, type(current_value)):
                    raise TypeError(f"[LeagueModel] Field '{key}' must be of type {type(current_value).__name__}, got {type(value).__name__}")

            safe_value = deepcopy(value) if isinstance(value, (dict, list)) else value
            setattr(self, key, safe_value)
            
    def to_meta_json(self) -> dict:
        return {
            "league_id": self.league_id,
            "league_title": self.league_title,
            "status": self.status,
        }

    def to_json(self) -> dict:
        return {
            "league_id": self.league_id,
            "league_administrator_id": self.league_administrator_id,
            "league_title": self.league_title,
            "league_budget": float(self.league_budget),
            "league_budget": self.league_budget,
            "league_description": self.league_description,
            "status": str(self.status),
            "registration_deadline": self.registration_deadline.isoformat() if self.registration_deadline else None,
            "opening_date": self.opening_date.isoformat() if self.opening_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "banner_url": self.banner_url if self.banner_url else None,
            "championship_trophies": [
                image.to_json() for image in self.championship_trophy_images
            ],
            "season_year": self.season_year,
            "categories": [assoc.to_json() for assoc in self.categories] if self.categories else [],
            "league_rules": self.league_rules,
            "sponsors": self.sponsors,
            "league_administrator": self.league_administrator.to_json() if self.league_administrator else None,
            "league_teams": [assoc.to_json() for assoc in self.league_teams] if self.league_teams else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    # use for founded_at
    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    
class LeagueTeamModel(db.Model):
    __tablename__ = 'league_teams_table'

    league_team_id = UUIDGenerator(db, 'league-team')
    team_id = db.Column(db.String, db.ForeignKey('teams_table.team_id'))
    league_id = db.Column(db.String, db.ForeignKey('leagues_table.league_id'))
    category_id = db.Column(db.String, db.ForeignKey('league_categories_table.category_id'))

    status = db.Column(db.Enum('Pending', 'Accepted', 'Rejected', name="league_team_status"), default='Pending')

    wins = db.Column(db.Integer, default=0, nullable=False)
    losses = db.Column(db.Integer, default=0, nullable=False)
    draws = db.Column(db.Integer, default=0, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.CheckConstraint('wins >= 0', name='check_wins_positive'),
        db.CheckConstraint('losses >= 0', name='check_losses_positive'),
        db.CheckConstraint('draws >= 0', name='check_draws_positive'),
        db.CheckConstraint('points >= 0', name='check_points_positive'),
    )

    team = db.relationship(
        'TeamModel',
        back_populates='league_team'
    )
    league = db.relationship('LeagueModel', back_populates='league_teams')
    category = db.relationship('LeagueCategoryModel', back_populates='category_teams')

    players = db.relationship(
        'LeaguePlayerModel',
        back_populates='league_team',
        cascade='all, delete-orphan'
    )
    
    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def team_to_json(self) -> dict:
        players = [player.to_json() for player in self.players]

        return {
            "league_team_id": self.league_team_id,
            "team_id": self.team_id,
            "status": self.status,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "points": self.points,
            "team_name": self.team.team_name,
            "team_address": self.team.team_address,
            "team_motto": self.team.team_motto,
            "team_logo_url": self.team.team_logo_url,
            "coach_name": self.team.coach_name,
            "assistant_coach_name": self.team.assistant_coach_name if self.team.assistant_coach_name else None,
            "team_captain": self.team.team_captain.to_json_for_team() if self.team.team_captain else None,
            "players": players,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
class LeaguePlayerModel(db.Model):
    __tablename__ = 'league_players_table'

    league_player_id = UUIDGenerator(db, 'league-player-id')

    player_team_id = db.Column(
        db.String,
        db.ForeignKey('player_team_table.player_team_id', ondelete='CASCADE'),
        nullable=False
    )

    league_team_id = db.Column(
        db.String,
        db.ForeignKey('league_teams_table.league_team_id', ondelete='CASCADE'),
        nullable=False
    )

    league_id = db.Column(
        db.String,
        db.ForeignKey('leagues_table.league_id'),
        nullable=False
    )

    league_team = db.relationship('LeagueTeamModel', back_populates='players')

    total_points = db.Column(db.Float, nullable=False, default=0.0)

    player_team = db.relationship(
        'PlayerTeamModel',
        backref=db.backref('league_players', cascade='all, delete-orphan')
    )

    is_ban = db.Column(db.Boolean, nullable=False, default=False)
    is_allowed = db.Column(db.Boolean, nullable=False, default=True)

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def to_json(self) -> dict:
        return {
            "league_player_id": self.league_player_id,
            "player_team_id": self.player_team_id,
            "league_team_id": self.league_team_id,
            "total_points": self.total_points,
            "league_id": self.league_id,
            "player_team": self.player_team.to_json_for_team() if self.player_team else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class LeagueCategoryModel(db.Model):
    __tablename__ = 'league_categories_table'

    category_id = UUIDGenerator(db, 'category')
    league_id = db.Column(
        db.String,
        db.ForeignKey('leagues_table.league_id', ondelete="CASCADE")
    )

    category_name = db.Column(db.String(100), nullable=False)

    category_teams = db.relationship('LeagueTeamModel', back_populates='category')

    category_format = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(100), nullable=False, default="Group Stage")
    max_team = db.Column(db.Integer, nullable=False, default=4)
    accept_teams = db.Column(db.Boolean, nullable=False, default=True)
    entrance_fee_amount = db.Column(db.Float, nullable=True, default=0.0)

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    league = db.relationship(
        'LeagueModel',
        back_populates='categories',
        passive_deletes=True
    )

    def to_json(self) -> dict:
        return {
            "category_id": self.category_id,
            "league_id": self.league_id,
            "category_name": self.category_name,
            "category_teams": [assoc.team.to_json() for assoc in self.category_teams] if self.category_teams else [],
            "max_team": self.max_team,
            "category_format": self.category_format,
            "accept_teams": self.accept_teams,
            "entrance_fee_amount": float(self.entrance_fee_amount) if self.entrance_fee_amount else 0.0,
            "stage": self.stage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

