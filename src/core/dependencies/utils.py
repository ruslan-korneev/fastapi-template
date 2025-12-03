import re

from fastapi import HTTPException, Query, status


def validated_uuid(value: str = Query(...)) -> str:
    """Validate UUID format."""
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if not re.match(uuid_pattern, value.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format",
        )
    return value.lower()


def validated_email(email: str = Query(...)) -> str:
    """Validate email format."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    return email.lower()


def validated_optional_email(email: str | None = Query(None)) -> str | None:
    """Validate optional email format."""
    if email is None:
        return None
    return validated_email(email)
