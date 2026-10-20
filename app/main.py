import logging

from fastapi import FastAPI
from nats import connect
from nats.aio.msg import Msg

from .callout_service import ScotAuthCalloutService
from .logging_utils import configure_logging
from .settings import (
    AUTH_CALLOUT_PASSWORD,
    AUTH_CALLOUT_USERNAME,
    LOG_LEVEL,
    NATS_AUTH_SUBJECT,
    NATS_HOST,
    NATS_PORT,
    NATS_PROTOCOL,
)

configure_logging()
logger = logging.getLogger("nats_auth_callout")

app = FastAPI()
_service = ScotAuthCalloutService()
_nc = None
_subscription = None


def _nats_server_url() -> str:
    return f"{NATS_PROTOCOL}://{NATS_HOST}:{NATS_PORT}"


async def _handle_auth_message(msg: Msg) -> None:
    try:
        response = await _service(msg.data)
        if msg.reply:
            await msg.respond(response.encode())
    except Exception as exc:
        logger.exception("callout handler failure type=%s", type(exc).__name__)
        if msg.reply:
            # Fail closed if we cannot process the request.
            await msg.respond(b"")


@app.on_event("startup")
async def startup_event():
    global _nc, _subscription
    logger.info("connecting to nats url=%s subject=%s log_level=%s", _nats_server_url(), NATS_AUTH_SUBJECT, LOG_LEVEL)
    _nc = await connect(
        servers=[_nats_server_url()],
        user=AUTH_CALLOUT_USERNAME,
        password=AUTH_CALLOUT_PASSWORD,
        connect_timeout=2,
    )
    _subscription = await _nc.subscribe(NATS_AUTH_SUBJECT, cb=_handle_auth_message)
    logger.info("auth callout subscription ready subject=%s", NATS_AUTH_SUBJECT)


@app.on_event("shutdown")
async def shutdown_event():
    global _nc, _subscription
    if _subscription is not None:
        await _subscription.unsubscribe()
        _subscription = None
    if _nc is not None:
        await _nc.drain()
        await _nc.close()
        _nc = None


@app.get("/healthz")
async def healthz():
    return {"ok": _nc is not None and _nc.is_connected}
