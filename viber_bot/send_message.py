import argparse
import json
import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.file_message import FileMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.url_message import URLMessage


def get_viber():
    return Api(BotConfiguration(
        name=os.environ.get("BOT_NAME", "EchoBot"),
        avatar=os.environ.get("BOT_AVATAR", ""),
        auth_token=os.environ["VIBER_AUTH_TOKEN"],
    ))


def parse_button(spec):
    if "=" not in spec:
        raise argparse.ArgumentTypeError(
            f"Button must be 'Label=action_body', got: {spec!r}"
        )
    label, action_body = spec.split("=", 1)
    return {
        "Columns": 6,
        "Rows": 1,
        "ActionType": "reply",
        "ActionBody": action_body,
        "Text": label,
        "TextSize": "regular",
    }


def build_message(args):
    if args.kind == "text":
        return TextMessage(text=args.text)
    if args.kind == "picture":
        return PictureMessage(media=args.image_url, text=args.caption, thumbnail=args.thumbnail)
    if args.kind == "url":
        return URLMessage(media=args.url)
    if args.kind == "file":
        return FileMessage(media=args.file_url, size=args.size, file_name=args.name)
    if args.kind == "keyboard":
        keyboard = {"Type": "keyboard", "Buttons": [parse_button(b) for b in args.button]}
        return TextMessage(text=args.text, keyboard=keyboard)
    raise ValueError(f"unknown kind: {args.kind}")


def main():
    parser = argparse.ArgumentParser(description="Send rich Viber messages to a subscribed user.")
    sub = parser.add_subparsers(dest="kind", required=True)

    p_text = sub.add_parser("text", help="Plain text message")
    p_text.add_argument("user_id")
    p_text.add_argument("text")

    p_pic = sub.add_parser("picture", help="Image message (JPEG, public HTTPS URL)")
    p_pic.add_argument("user_id")
    p_pic.add_argument("image_url")
    p_pic.add_argument("--caption", default="")
    p_pic.add_argument("--thumbnail", default=None)

    p_url = sub.add_parser("url", help="Clickable URL message")
    p_url.add_argument("user_id")
    p_url.add_argument("url")

    p_file = sub.add_parser("file", help="File message")
    p_file.add_argument("user_id")
    p_file.add_argument("file_url")
    p_file.add_argument("--size", type=int, required=True, help="File size in bytes")
    p_file.add_argument("--name", required=True, help="File name including extension")

    p_kb = sub.add_parser("keyboard", help="Text message with reply buttons")
    p_kb.add_argument("user_id")
    p_kb.add_argument("text")
    p_kb.add_argument(
        "--button",
        action="append",
        required=True,
        help="Reply button as 'Label=action_body'. Repeat for multiple buttons.",
    )

    args = parser.parse_args()
    viber = get_viber()
    tokens = viber.send_messages(args.user_id, [build_message(args)])
    print(json.dumps({"tokens": tokens}, default=str))


if __name__ == "__main__":
    main()
