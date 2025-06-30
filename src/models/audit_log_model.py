from src.models.league_administrator_model import LeagueAdministratorModel
from src.models.league_model import LeagueModel
from src.models.player_model import PlayerModel
from src.models.team_model import TeamModel
from src.models.user_model import UserModel
from src.utils.api_response import ApiResponse
from src.utils.db_utils import AccountTypeEnum, CreatedAt, UUIDGenerator, create_account_type_enum
from src.extensions import db
from flask import request
from typing import Optional

class AuditLogModel(db.Model):
    __tablename__ = 'audit_logs'

    audit_id = UUIDGenerator(db, 'audit')
    timestamp = CreatedAt(db)

    audit_by_id = db.Column(db.String, nullable=False)
    audit_by_type = db.Column(create_account_type_enum(db), nullable=False)

    audit_to_id = db.Column(db.String, nullable=False)
    audit_to_type = db.Column(create_account_type_enum(db), nullable=False)

    action = db.Column(db.String(100), nullable=False)  
    details = db.Column(db.String, nullable=True)

    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    def to_json(self):
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat(),
            "audit_by_id": self.audit_by_id,
            "audit_by_type": self.audit_by_type,
            "auditor_obj": self.get_auditor_json(),
            "action": self.action,
            "details": self.details,
            "is_read": self.is_read,
            "read_at": self.isoformat()
        }

    def get_auditor_json(self) -> Optional[dict]:
        if self.audit_by_type == AccountTypeEnum.PLAYER.value:
            a = PlayerModel.query.get(self.audit_by_id)
            return a.to_json()
        elif self.audit_by_type == AccountTypeEnum.TEAM_CREATOR.value:
            a = UserModel.query.get(self.audit_by_id)
            return a.to_json()
        elif self.audit_by_type == AccountTypeEnum.LOCAL_ADMINISTRATOR.value or self.audit_by_type == AccountTypeEnum.LGU_ADMINISTRATOR.value:
            a = LeagueAdministratorModel.query.get(self.audit_by_id)
            return a.to_json_for_log()
        return None

    @staticmethod
    def log_action(audit_to_id, audit_to_type, action, details=None, audit_by_id=None, audit_by_type=None):
        if not audit_by_id:
            audit_by_id = request.remote_addr
        
        if not audit_by_type:
            audit_by_type = AccountTypeEnum.SYSTEM.value

        audit_entry = AuditLogModel(
            audit_by_id=audit_by_id,
            audit_by_type=audit_by_type,
            audit_to_id=audit_to_id,
            audit_to_type=audit_to_type,
            action=action,
            details=details
        )
        db.session.add(audit_entry)
        db.session.commit()

    @staticmethod
    def fetch_log(audit_id):
        try:
            audit = AuditLogModel.query.get(audit_id)
            payload = audit.to_json()
            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.error(str(e))
        
    @staticmethod
    def fetch_logs_for(audit_to_id):
        try:
            audits = AuditLogModel.query.filter(AuditLogModel.audit_to_id == audit_to_id).all()
            payload = [audit.to_json() for audit in audits]
            return ApiResponse.success(payload=payload)
        except Exception as e:
            return ApiResponse.success(payload=[])