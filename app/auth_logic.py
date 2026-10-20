from .models import AuthDecision, WhoAmIResponse
from .settings import (
    API_SERVICE_PASSWORD,
    API_SERVICE_PUBLISH_SUBJECTS,
    API_SERVICE_SUBSCRIBE_SUBJECTS,
    API_SERVICE_USERNAME,
    FLAIR_SERVICE_PASSWORD,
    FLAIR_SERVICE_PUBLISH_SUBJECTS,
    FLAIR_SERVICE_SUBSCRIBE_SUBJECTS,
    FLAIR_SERVICE_USERNAME,
    NATS_IRELEMENT_SUBJECT,
    NATS_NOTIFICATION_BROADCAST_SUBJECT,
    NATS_SUBJECT_ROOT,
)


SERVICE_ACCOUNTS = {
    API_SERVICE_USERNAME: AuthDecision(
        allow=True,
        username=API_SERVICE_USERNAME,
        publish=API_SERVICE_PUBLISH_SUBJECTS,
        subscribe=API_SERVICE_SUBSCRIBE_SUBJECTS,
    ),
    FLAIR_SERVICE_USERNAME: AuthDecision(
        allow=True,
        username=FLAIR_SERVICE_USERNAME,
        publish=FLAIR_SERVICE_PUBLISH_SUBJECTS,
        subscribe=FLAIR_SERVICE_SUBSCRIBE_SUBJECTS,
    ),
}

SERVICE_PASSWORDS = {
    API_SERVICE_USERNAME: API_SERVICE_PASSWORD,
    FLAIR_SERVICE_USERNAME: FLAIR_SERVICE_PASSWORD,
}


def authorize_service_user(username: str | None, password: str | None) -> AuthDecision | None:
    if not username:
        return None

    decision = SERVICE_ACCOUNTS.get(username)
    expected_password = SERVICE_PASSWORDS.get(username)

    if decision is None:
        return None

    if not expected_password or password != expected_password:
        return AuthDecision(
            allow=False,
            reason="invalid_service_password",
        )

    return decision.model_copy(deep=True)


def authorize_user(user: WhoAmIResponse | None) -> AuthDecision:
    if user is None:
        return AuthDecision(
            allow=False,
            reason="whoami_failed_or_invalid",
        )

    if not user.is_active:
        return AuthDecision(
            allow=False,
            reason="inactive_user",
        )

    if not user.username:
        return AuthDecision(
            allow=False,
            reason="missing_username",
        )

    if user.id is None:
        return AuthDecision(
            allow=False,
            reason="missing_user_id",
        )

    return AuthDecision(
        allow=True,
        username=user.username,
        publish=[],
        subscribe=[
            NATS_IRELEMENT_SUBJECT,
            f"{NATS_SUBJECT_ROOT}.notification.user.{user.id}.>",
            NATS_NOTIFICATION_BROADCAST_SUBJECT,
        ],
    )
