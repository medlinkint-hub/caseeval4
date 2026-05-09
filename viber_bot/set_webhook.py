import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration


def main():
    viber = Api(BotConfiguration(
        name=os.environ.get("BOT_NAME", "EchoBot"),
        avatar=os.environ.get("BOT_AVATAR", ""),
        auth_token=os.environ["VIBER_AUTH_TOKEN"],
    ))
    webhook_url = os.environ["WEBHOOK_URL"]
    event_types = viber.set_webhook(webhook_url)
    print(f"Webhook registered at {webhook_url}")
    print(f"Subscribed events: {event_types}")


if __name__ == "__main__":
    main()
