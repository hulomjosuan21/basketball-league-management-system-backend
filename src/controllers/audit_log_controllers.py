from backend.src.utils.db_utils import AccountTypeEnum
from src.models.audit_log_model import AuditLogModel
from src.extensions import db
from src.utils.api_response import ApiResponse
from flask import request
class AuditLogControllers:
    def set_isread(self, audit_to_id: str, is_read: bool):
        try:
            audit = AuditLogModel.query.filter_by(audit_to_id=audit_to_id).first()
            audit.is_read = is_read
            db.session.commit()

            return ApiResponse.success()
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    def create(self):
        try:
            data = request.get_json()

            new_log = AuditLogModel(
                audit_by_id=data['audit_by_id'],
                audit_by_type=AccountTypeEnum(data['audit_by_type']),
                audit_to_id=data['audit_to_id'],
                audit_to_type=AccountTypeEnum(data['audit_to_type']),
                action=data['action'],
                details=data.get('details', None),
                is_read=False,
                read_at=None,
            )

            db.session.add(new_log)
            db.session.commit()

            return ApiResponse.success(message="Audit log created")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))