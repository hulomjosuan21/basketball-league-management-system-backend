from src.utils.db_utils import CreatedAt, UUIDGenerator, UpdatedAt
from src.extensions import db

class LeagueAdministratorModel(db.Model):
    __tablename__ = 'league_administrator_table'

    league_administrator_id = UUIDGenerator(db,'league_administrator')

    is_allowed = db.Column(db.Boolean, nullable=False, default=False)
    is_operational = db.Column(db.Boolean, nullable=False, default=True)

    user_id = db.Column(
        db.String,
        db.ForeignKey('users_table.user_id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )

    organization_type = db.Column(
        db.String,
        nullable=False
    )

    @property
    def active_league(self):
        return next(
            (
                league for league in self.created_leagues
                if league.status not in ('Completed', 'Postponed', 'Cancelled')
            ),
            None
        )

    organization_name = db.Column(
        db.String(200),
        nullable=False
    )

    contact_number = db.Column(
        db.String(15),
        nullable=True
    )

    organization_address = db.Column(
        db.String(250),
        nullable=False
    )

    organization_photo_url = db.Column(
        db.String,
        nullable=True
    )

    organization_logo_url = db.Column(
        db.String,
        nullable=True
    )

    user = db.relationship(
        'UserModel',
        back_populates='league_administrator',
        cascade='all, delete-orphan',
        single_parent=True
    )

    created_leagues = db.relationship(
            'LeagueModel',
            back_populates='league_administrator',
            cascade='all, delete-orphan',
            passive_deletes=True
        )

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)

    def to_json_for_log(self) -> dict:
        return {
            "league_administrator_id": self.league_administrator_id,
            "user_id": self.user_id,
            "organization_type": self.organization_type,
            "organization_name": self.organization_name,
            "organization_address": self.organization_address,
            "organization_logo_url": self.organization_logo_url,
        }

    def to_json(self) -> dict:
        return {
            "league_administrator_id": self.league_administrator_id,
            "is_allowed": self.is_allowed,
            "is_operational": self.is_operational,
            "user_id": self.user_id,
            "organization_type": self.organization_type,
            "organization_name": self.organization_name,
            "organization_address": self.organization_address,
            "organization_photo_url": self.organization_photo_url,
            "organization_logo_url": self.organization_logo_url,
            "user": self.user.to_json() if self.user else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }