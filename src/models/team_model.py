from src.utils.db_utils import CreatedAt, UUIDGenerator, UpdatedAt
from src.extensions import db
from src.utils.mixins import UpdatableMixin

class PlayerTeamModel(db.Model):
    __tablename__ = 'player_team_table'

    player_team_id = UUIDGenerator(db, 'player-team')

    player_id = db.Column(db.String, db.ForeignKey('players_table.player_id'), nullable=False)
    team_id = db.Column(db.String, db.ForeignKey('teams_table.team_id', ondelete="CASCADE"), nullable=False)
    is_ban = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint('player_id', 'team_id', name='unique_player_team'),
    )

    # Relationships
    player = db.relationship('PlayerModel', back_populates='my_teams')
    team = db.relationship(
        'TeamModel',
        back_populates='players',
        foreign_keys=[team_id]
    )

    is_accepted = db.Column(
        db.Enum('Pending', 'Accepted', 'Rejected', 'Invited', name="player_is_accepted"),
        nullable=False,
        default="Pending"
    )

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def to_json(self) -> dict:
        return {
            "player_team_id": self.player_team_id,
            "player_id": self.player_id,
            "team_id": self.team_id,
            "player": self.player.to_json_for_team() if self.player else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class TeamModel(db.Model, UpdatableMixin):
    __tablename__ = 'teams_table'

    team_id = UUIDGenerator(db, 'team')

    user_id = db.Column(
        db.String,
        db.ForeignKey('users_table.user_id', ondelete='CASCADE'),
        nullable=False
    )
    user = db.relationship('UserModel', back_populates='teams', single_parent=True)

    team_name = db.Column(db.String(100), nullable=False)
    team_address = db.Column(db.String(250), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    team_motto = db.Column(db.String(100), nullable=True)
    team_logo_url = db.Column(db.String, nullable=False)
    championships_won = db.Column(db.Integer, nullable=False, default=0)
    coach_name = db.Column(db.String(100), nullable=False)
    assistant_coach_name = db.Column(db.String(100), nullable=True)

    total_wins = db.Column(db.Integer, default=0, nullable=False)
    total_losses = db.Column(db.Integer, default=0, nullable=False)
    is_recruiting = db.Column(db.Boolean, nullable=False, default=False)
    team_category = db.Column(db.String(100), nullable=True)

    team_captain_id = db.Column(db.String, nullable=True)

    # @property
    # def team_captain(self):
    #     from src.models.player_team_model import PlayerTeamModel  # Avoid circular import
    #     if self.team_captain_id:
    #         return db.session.get(PlayerTeamModel, self.team_captain_id)
    #     return None

    # def players_to_json_list(self):
    #     return [player.to_json_for_team() for player in self.players] if self.players else []

    def to_json_for_notification(self, detail):
        return {
            'team_id': self.team_id,
            'team_logo_url': self.team_logo_url if self.team_logo_url else None,
            'team_name': self.team_name,
            'detail': detail
        }

    def to_json_for_join_league(self):
        return {
            "team_id": self.team_id,
            "user_id": self.user_id,
            "team_name": self.team_name,
            "team_logo_url": self.team_logo_url if self.team_logo_url else None,
            "already_in": None,
            "status": None
        }

    def to_json(self):
        # team_captain = self.team_captain.to_json_for_team() if self.team_captain else None

        return {
            "team_id": self.team_id,
            "user_id": self.user_id,
            "team_name": self.team_name,
            "team_address": self.team_address,
            "contact_number": self.contact_number,
            "team_motto": self.team_motto if self.team_motto else None,
            "team_logo_url": self.team_logo_url if self.team_logo_url else None,
            "championships_won": self.championships_won,
            "coach_name": self.coach_name,
            "team_category": self.team_category if self.team_category else None,
            "assistant_coach_name": self.assistant_coach_name if self.assistant_coach_name else None,
            # "team_captain": team_captain,
            "total_wins": self.total_wins,
            "is_recruiting": self.is_recruiting,
            "total_losses": self.total_losses,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    players = db.relationship(
        'PlayerTeamModel',
        back_populates='team',
        cascade='all, delete-orphan',
        foreign_keys='PlayerTeamModel.team_id',
        passive_deletes=True
    )

    payments = db.relationship('PaymentModel', back_populates='team', cascade="all, delete-orphan")

    league_team = db.relationship(
        'LeagueTeamModel',
        back_populates='team',
        cascade='all, delete-orphan'
    )

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)