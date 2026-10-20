import os


def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


WHOAMI_URL = os.getenv(
    "WHOAMI_URL",
    "http://scot4-api-service:8000/api/v1/users/whoami",
)
WHOAMI_TIMEOUT_SECONDS = float(os.getenv("WHOAMI_TIMEOUT_SECONDS", "2.0"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def _subject_root() -> str:
    root = os.getenv("NATS_SUBJECT_ROOT")
    if root:
        return root.strip(".").lower()

    legacy_prefix = os.getenv("NATS_SUBJECT_PREFIX", "")
    if legacy_prefix.lower().startswith("scot."):
        return legacy_prefix.split(".", 1)[0].lower()

    return "scot"


NATS_SUBJECT_ROOT = _subject_root()
NATS_IRELEMENT_SUBJECT = f"{NATS_SUBJECT_ROOT}.irelement.>"
NATS_NOTIFICATION_SUBJECT = f"{NATS_SUBJECT_ROOT}.notification.>"
NATS_NOTIFICATION_BROADCAST_SUBJECT = f"{NATS_SUBJECT_ROOT}.notification.broadcast.>"
NATS_FLAIR_REGEX_SUBJECT = f"{NATS_SUBJECT_ROOT}.flair.regex.>"
NATS_FLAIR_JOB_SUBJECT = f"{NATS_SUBJECT_ROOT}.flair.job.>"
# Backward-compatible name for existing imports and older templates.
NATS_SUBJECT_PREFIX = NATS_IRELEMENT_SUBJECT

NATS_PROTOCOL = os.getenv("NATS_PROTOCOL", "nats")
NATS_HOST = os.getenv("NATS_HOST", "scot4-nats")
NATS_PORT = int(os.getenv("NATS_PORT", "4222"))
NATS_AUTH_SUBJECT = os.getenv("NATS_AUTH_SUBJECT", "$SYS.REQ.USER.AUTH")
NATS_AUTH_ACCOUNT = os.getenv("NATS_AUTH_ACCOUNT", "$G")

AUTH_CALLOUT_USERNAME = os.getenv("AUTH_CALLOUT_USERNAME", "auth_callout_service")
AUTH_CALLOUT_PASSWORD = os.getenv("AUTH_CALLOUT_PASSWORD", "")
API_SERVICE_USERNAME = os.getenv("API_SERVICE_USERNAME", "api_service")
API_SERVICE_PASSWORD = os.getenv("API_SERVICE_PASSWORD", "")
FLAIR_SERVICE_USERNAME = os.getenv("FLAIR_SERVICE_USERNAME", "flair_service")
FLAIR_SERVICE_PASSWORD = os.getenv("FLAIR_SERVICE_PASSWORD", "")
NATS_AUTH_ISSUER_SEED = os.getenv("NATS_AUTH_ISSUER_SEED", "")

API_SERVICE_PUBLISH_SUBJECTS = _csv_env(
    "API_SERVICE_PUBLISH_SUBJECTS",
    f"{NATS_IRELEMENT_SUBJECT},{NATS_NOTIFICATION_SUBJECT},{NATS_FLAIR_REGEX_SUBJECT},{NATS_FLAIR_JOB_SUBJECT}",
)
API_SERVICE_SUBSCRIBE_SUBJECTS = _csv_env(
    "API_SERVICE_SUBSCRIBE_SUBJECTS",
    f"{NATS_IRELEMENT_SUBJECT},{NATS_NOTIFICATION_SUBJECT}",
)
FLAIR_SERVICE_PUBLISH_SUBJECTS = _csv_env("FLAIR_SERVICE_PUBLISH_SUBJECTS")
FLAIR_SERVICE_SUBSCRIBE_SUBJECTS = _csv_env(
    "FLAIR_SERVICE_SUBSCRIBE_SUBJECTS",
    f"{NATS_SUBJECT_PREFIX},{NATS_FLAIR_REGEX_SUBJECT},{NATS_FLAIR_JOB_SUBJECT}",
)
