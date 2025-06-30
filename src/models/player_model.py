from src.extensions import db, ph
from src.utils.db_utils import CreatedAt, UUIDGenerator, UpdatedAt

class PlayerModel(db.Model):
    __tablename__ = 'players_table'

    player_id = UUIDGenerator(db,'player')
    
    user_id = db.Column(
        db.String,
        db.ForeignKey('users_table.user_id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )

    full_name = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    player_address = db.Column(
        db.String(250),
        nullable=False
    )

    jersey_name = db.Column(db.String(1000), nullable=False)
    jersey_number = db.Column(db.Float, nullable=False)
    position = db.Column(db.String(250), nullable=False)

    height_in = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    
    games_played = db.Column(db.Integer, default=0, nullable=False)
    points_scored = db.Column(db.Integer, default=0, nullable=False)
    assists = db.Column(db.Integer, default=0, nullable=False)
    rebounds = db.Column(db.Integer, default=0, nullable=False)

    profile_image_url = db.Column(db.String(1000), nullable=False)
    document_url_1 = db.Column(db.String(1000), nullable=True)
    document_url_2 = db.Column(db.String(1000), nullable=True)

    is_ban = db.Column(db.Boolean, nullable=False, default=False)
    is_allowed = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship(
        'UserModel',
        back_populates='player',
        cascade='all, delete-orphan',
        single_parent=True
    )

    my_teams = db.relationship('PlayerTeamModel', back_populates='player', cascade='all, delete-orphan')

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def to_json(self) -> dict:
        return {
            "player_id": self.player_id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "gender": self.gender,
            "birth_date": self.birth_date.isoformat(),
            "player_address": self.player_address,
            "jersey_name": self.jersey_name,
            "jersey_number": float(self.jersey_number) if self.jersey_number is not None else None,
            "position": self.position,
            "height_in": float(self.height_in) if self.height_in is not None else None,
            "weight_kg": float(self.weight_kg) if self.weight_kg is not None else None,
            "games_played": int(self.games_played),
            "points_scored": int(self.points_scored),
            "assists": int(self.assists),
            "rebounds": int(self.rebounds),
            "profile_image_url": self.profile_image_url,
            "document_url_1": self.document_url_1 if self.created_at else None,
            "document_url_2": self.document_url_2 if self.created_at else None,
            "user": self.user.to_json() if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
