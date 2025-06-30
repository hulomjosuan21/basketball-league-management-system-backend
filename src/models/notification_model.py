from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from src.utils.enums import NotificationAction
from src.utils.db_utils import AccountTypeEnum, CreatedAt, UUIDGenerator, create_account_type_enum
from src.extensions import db

class NotificationModel(db.Model):
    __tablename__ = 'notifications_table'

    notification_id = UUIDGenerator(db,'notifications')

    # Common fields
    author = Column(db.String, nullable=False)
    detail = Column(db.String, nullable=False)
    image = Column(db.String, nullable=True)
    account_type = Column(create_account_type_enum(db), nullable=True)
    timestamp = CreatedAt(db)
    action = Column(db.JSON, nullable=True)

    # Optional team-related fields
    team_id = Column(db.String, nullable=True)
    team_name = Column(db.String, nullable=True)
    team_logo_url = Column(db.String, nullable=True)

    user_id = Column(db.String, ForeignKey('users_table.user_id'), nullable=False)

    def to_json(self):
        is_team_invite = (
            self.action and
            self.action.get('type') == NotificationAction.PLAYER_INVITATION.value
        )

        json_data = {
            'notification_id': self.notification_id,
            'author': self.author,
            'detail': self.detail,
            'image': self.image,
            'timestamp': self.timestamp.isoformat(),
            'account_type': str(self.account_type) if self.account_type else None,
            'action': self.action,
        }

        if is_team_invite:
            json_data.update({
                'team_id': self.team_id,
                'team_name': self.team_name,
                'team_logo_url': self.team_logo_url,
            })

        return json_data

    @staticmethod
    def from_message(author: str, detail: str, user_id: str, image: str = None, account_type=None, action: dict = None):
        return NotificationModel(
            author=author,
            detail=detail,
            image=image,
            account_type=account_type,
            action=action,
            user_id=user_id
        )

    @staticmethod
    def from_team_invite(team, action, detail: str, user_id: str):
        return NotificationModel(
            author=team.team_name,
            detail=detail,
            image=team.team_logo_url,
            account_type=AccountTypeEnum.TEAM_CREATOR.value,
            action=action,
            team_id=team.team_id,
            team_name=team.team_name,
            team_logo_url=team.team_logo_url,
            user_id=user_id
        )
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.notification_id
