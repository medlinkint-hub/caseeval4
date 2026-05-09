import logging
import os

from flask import Flask, Response, request
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (
    ViberConversationStartedRequest,
    ViberFailedRequest,
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberUnsubscribedRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

viber = Api(BotConfiguration(
    name=os.environ.get("BOT_NAME", "EchoBot"),
    avatar=os.environ.get("BOT_AVATAR", ""),
    auth_token=os.environ["VIBER_AUTH_TOKEN"],
))


@app.route("/", methods=["POST"])
def incoming():
    signature = request.headers.get("X-Viber-Content-Signature", "")
    body = request.get_data()

    if not viber.verify_signature(body, signature):
        return Response(status=403)

    viber_request = viber.parse_request(body)

    if isinstance(viber_request, ViberMessageRequest):
        text = getattr(viber_request.message, "text", "") or ""
        viber.send_messages(viber_request.sender.id, [
            TextMessage(text=f"You said: {text}"),
        ])

    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.user.id, [
            TextMessage(text=f"Hi {viber_request.user.name}, welcome!"),
        ])

    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [
            TextMessage(text=f"Thanks for subscribing, {viber_request.user.name}!"),
        ])

    elif isinstance(viber_request, ViberUnsubscribedRequest):
        logger.info("User unsubscribed: %s", viber_request.user_id)

    elif isinstance(viber_request, ViberFailedRequest):
        logger.warning("Failed delivery: %s", viber_request)

    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))
