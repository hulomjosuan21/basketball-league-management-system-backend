from src.extensions import db, ph
from sqlalchemy import Enum as SqlEnum
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.utils.db_utils import AccountTypeEnum, CreatedAt, UUIDGenerator, UpdatedAt, create_account_type_enum
from argon2.exceptions import HashingError
import re

class UserModel(db.Model):
    __tablename__ = 'users_table'
    
    user_id = UUIDGenerator(db,'user')

    email = db.Column(db.String(120), unique=True, nullable=False)

    contact_number = db.Column(
        db.String(15),
        nullable=False,
    )

    password_hash = db.Column(db.String, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    account_type = db.Column(create_account_type_enum(db), nullable=False)
    fcm_token = db.Column(db.Text, nullable=True)

    def set_password(self, password_str: str) -> None:
        # if len(password_str) < 8:
        #     raise ValueError("Password must be at least 8 characters long.")
        # if not re.search(r"[A-Z]", password_str):
        #     raise ValueError("Password must include at least one uppercase letter.")
        # if not re.search(r"[a-z]", password_str):
        #     raise ValueError("Password must include at least one lowercase letter.")
        # if not re.search(r"[0-9]", password_str):
        #     raise ValueError("Password must include at least one digit.")
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password_str):
        #     raise ValueError("Password must include at least one special character (!@#$%^&*(),.?\":{}|<>).")
        try:
            self.password_hash = ph.hash(password_str)
        except HashingError as e:
            raise ValueError(f"Password hashing failed: {str(e)}")

    def verify_password(self, password_str: str) -> bool:
        try:
            return ph.verify(self.password_hash, password_str)
        except Exception:
            return False
        
    def to_json(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "contact_number": self.contact_number,
            "is_verified": self.is_verified,
            "account_type": self.account_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    league_administrator = db.relationship(
        'LeagueAdministratorModel',
        back_populates='user',
        cascade='all, delete-orphan',
        uselist=False,
        single_parent=True
    )

    # one to one
    player = db.relationship(
        'PlayerModel',
        back_populates='user',
        cascade='all, delete-orphan',
        uselist=False,
        single_parent=True
    )
    
    # one to many
    teams = db.relationship(
        'TeamModel',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def teams_to_json(self) -> list:
        return [team.to_json for team in self.teams]

    created_at = CreatedAt(db)
    updated_at = UpdatedAt(db)
