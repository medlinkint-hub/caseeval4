import argparse
import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage


def main():
    parser = argparse.ArgumentParser(description="Send a Viber message to a subscribed user.")
    parser.add_argument("user_id", help="Viber user ID (received via webhook events)")
    parser.add_argument("text", help="Message text to send")
    args = parser.parse_args()

    viber = Api(BotConfiguration(
        name=os.environ.get("BOT_NAME", "EchoBot"),
        avatar=os.environ.get("BOT_AVATAR", ""),
        auth_token=os.environ["VIBER_AUTH_TOKEN"],
    ))

    tokens = viber.send_messages(args.user_id, [TextMessage(text=args.text)])
    print(f"Sent. Message tokens: {tokens}")


if __name__ == "__main__":
    main()
