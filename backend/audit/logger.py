from datetime import datetime


def audit_log(
    user,
    endpoint,
    action,
    status,
    ip
):

    print({

        "timestamp": datetime.utcnow(),

        "user": user,

        "endpoint": endpoint,

        "action": action,

        "status": status,

        "ip": ip

    })