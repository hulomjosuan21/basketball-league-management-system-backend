from flask import Blueprint
from src.controllers.audit_log_controllers import AuditLogControllers
audit_log_bp = Blueprint('audit_log', __name__, url_prefix='/audit-log')

auditLogControllers = AuditLogControllers()

audit_log_bp.patch('/set-isread/<string:audit_to_id>/<string:is_read>')(
    lambda audit_to_id, is_read: auditLogControllers.set_isread(
        audit_to_id, is_read.lower() == 'true'
    )
)

audit_log_bp.post('/create')(auditLogControllers.create)
