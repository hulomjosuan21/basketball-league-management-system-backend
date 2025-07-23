from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum

from src.extensions import db
from sqlalchemy.orm import scoped_session, sessionmaker

def get_new_session():
    engine = db.get_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def CreatedAt(db):
    return db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

def UpdatedAt(db):
    return db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

def UUIDGenerator(db, prefix):
    def generate_uid():
        return f"{prefix}-{uuid.uuid4()}"
    return db.Column(
        db.String,
        primary_key=True,
        default=generate_uid
    )

class AccountTypeEnum(Enum):
    PLAYER = "Player"
    TEAM_CREATOR = "Team_Creator"
    LOCAL_ADMINISTRATOR = "League_Administrator_Local"
    LGU_ADMINISTRATOR = "League_Administrator_LGU"
    TEAM_MANAGER = "Team_Manager"
    SYSTEM = "System"

def create_account_type_enum(db):
    return db.Enum(
        *(member.value for member in AccountTypeEnum),
        name="account_type_enum"
    )