from fastapi import HTTPException


def require_role(allowed_roles):
    def checker(user):

        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access Denied"
            )

        return user

    return checker