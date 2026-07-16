from datetime import datetime
from database.database import SessionLocal
from database.models import AuditLog


def audit_log(user_id, endpoint, action, status, ip):

    db = SessionLocal()

    log = AuditLog(
        user_id=user_id,
        endpoint=endpoint,
        action=action,
        status=status,
        ip_address=ip,
        timestamp=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.close()