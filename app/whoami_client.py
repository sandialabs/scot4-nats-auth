import httpx

from .models import WhoAmIResponse
from .settings import WHOAMI_TIMEOUT_SECONDS, WHOAMI_URL


def build_whoami_authorization_header(credential: str) -> str:
    value = credential.strip()
    if not value:
        raise ValueError("missing credential")

    parts = value.split(None, 1)
    scheme = parts[0].lower()
    if scheme in {"bearer", "apikey"}:
        if len(parts) != 2 or not parts[1].strip():
            if scheme == "bearer":
                raise ValueError("missing bearer token")
            raise ValueError("missing apikey value")
        normalized_value = parts[1].strip()
        if scheme == "bearer":
            return f"Bearer {normalized_value}"
        return f"apikey {normalized_value}"

    # Backward compatibility for existing clients that send a raw bearer token.
    return f"Bearer {value}"


async def fetch_whoami(credential: str) -> WhoAmIResponse | None:
    headers = {
        "Authorization": build_whoami_authorization_header(credential),
    }

    async with httpx.AsyncClient(timeout=WHOAMI_TIMEOUT_SECONDS) as client:
        resp = await client.get(WHOAMI_URL, headers=headers)

        if resp.status_code != 200:
            return None

        data = resp.json()

        try:
            return WhoAmIResponse.model_validate(data)
        except Exception:
            return None
