import json
import logging
from typing import Any

from nats_callout import AuthError, BaseAuthCalloutService
from nats_callout.claims import AuthRequestData, UserData
from nats_callout.claims.user import PubSubPermissions
from nats_callout.encoder import AdaptixEncoder

from .auth_logic import authorize_service_user, authorize_user
from .models import AuthDecision
from .settings import NATS_AUTH_ACCOUNT, NATS_AUTH_ISSUER_SEED
from .whoami_client import fetch_whoami

logger = logging.getLogger("nats_auth_callout")

DENY_ALL_SUBJECTS = [">"]


def _subject_permissions(allow: list[str]) -> PubSubPermissions:
    """Translate an empty allow list into NATS' explicit deny-all form."""
    return PubSubPermissions(
        allow=allow,
        deny=[] if allow else DENY_ALL_SUBJECTS.copy(),
    )


def _user_data(decision: AuthDecision) -> UserData:
    return UserData(
        pub=_subject_permissions(decision.publish),
        sub=_subject_permissions(decision.subscribe),
    )


class CompatAdaptixEncoder(AdaptixEncoder):
    def __init__(self, kp):
        super().__init__()
        self.kp = kp
        self.json_dumps = json.dumps
        self.json_loads = self._json_loads_compat

    @staticmethod
    def _json_loads_compat(value: Any):
        if isinstance(value, (dict, list)):
            return value
        return json.loads(value)


class ScotAuthCalloutService(BaseAuthCalloutService):
    def __init__(self):
        self.nkey_seed = NATS_AUTH_ISSUER_SEED
        self.account = NATS_AUTH_ACCOUNT
        self.encoder = CompatAdaptixEncoder(self._key_pair)

    async def _handle_auth_request_data(self, auth_request_data: AuthRequestData) -> UserData:
        connect_opts = auth_request_data.connect_opts
        token = connect_opts.auth_token or connect_opts.jwt
        username = connect_opts.user or auth_request_data.client_info.user
        password = connect_opts.pass_

        if token:
            try:
                user = await fetch_whoami(token)
            except Exception as exc:
                logger.warning("deny reason=whoami_exception detail=%s", type(exc).__name__)
                raise AuthError("whoami_exception") from exc
            decision = authorize_user(user)
        else:
            decision = authorize_service_user(username, password)
            if decision is None:
                raise AuthError("missing_credentials")

        if not decision.allow:
            raise AuthError(decision.reason or "denied")

        logger.info(
            "allow username=%s sub=%s pub=%s",
            decision.username,
            decision.subscribe,
            decision.publish,
        )

        return _user_data(decision)
