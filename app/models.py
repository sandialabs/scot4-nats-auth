from typing import Any, List, Optional

from pydantic import BaseModel


class WhoAmIResponse(BaseModel):
    username: str
    failed_attempts: int | None = None
    is_active: bool
    fullname: str | None = None
    email: str | None = None
    preferences: dict[str, Any] | None = None
    is_superuser: bool | None = None
    id: int
    roles: list[Any] | None = None
    last_login: str | None = None
    last_activity: str | None = None


class AuthDecision(BaseModel):
    allow: bool
    username: Optional[str] = None
    publish: List[str] = []
    subscribe: List[str] = []
    reason: Optional[str] = None
