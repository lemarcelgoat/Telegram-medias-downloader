import argparse
import asyncio
import getpass
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
import qrcode
from tqdm import tqdm
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import PeerChannel

LINK_RE = re.compile(
    r"(?:https?://)?t\.me/"
    r"(?:"
    r"c/(?P<cid>\d+)/(?P<cmsgid>\d+)(?:/(?P<cmsgid2>\d+))?"
    r"|(?P<username>(?!c/)[A-Za-z0-9_]+)/(?P<msgid>\d+)(?:/(?P<msgid2>\d+))?"
    r")",
    re.IGNORECASE,
)


def parse_link(link: str):
    match = LINK_RE.search(link.strip())
    if not match:
        return None
    if match.group("username"):
        msg_id = match.group("msgid2") or match.group("msgid")
        return ("username", match.group("username"), int(msg_id))
    msg_id = match.group("cmsgid2") or match.group("cmsgid")
    return ("c", int(match.group("cid")), int(msg_id))


def sanitize_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value or "telegram"


def sanitize_phone(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[()\s-]+", "", value)
    if value.startswith("00"):
        value = f"+{value[2:]}"
    return value


def load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def log_event(log_path: Path | None, payload: dict) -> None:
    if not log_path:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def fmt_mb(value: int) -> str:
    return f"{value / (1024 * 1024):.2f} MB"


def is_image_or_video_message(message) -> bool:
    if getattr(message, "photo", None):
        return True
    if getattr(message, "video", None):
        return True
    document = getattr(message, "document", None)
    if document and getattr(message, "file", None):
        mime = message.file.mime_type or ""
        return mime.startswith("image/") or mime.startswith("video/")
    return False


def media_kind(message) -> str:
    if getattr(message, "photo", None):
        return "image"
    if getattr(message, "video", None):
        return "video"
    document = getattr(message, "document", None)
    if document and getattr(message, "file", None):
        mime = message.file.mime_type or ""
        if mime.startswith("image/"):
            return "image"
        if mime.startswith("video/"):
            return "video"
    return "autre"


def build_output_dir(base: Path, entity, msg_id: int, topic_title: str | None) -> Path:
    label = (
        getattr(entity, "username", None)
        or getattr(entity, "title", None)
        or str(getattr(entity, "id", "chat"))
    )
    label = sanitize_name(str(label))
    if topic_title:
        return base / label / sanitize_name(topic_title)
    return base / label / str(msg_id)


def build_channel_root(base: Path, entity) -> Path:
    label = (
        getattr(entity, "username", None)
        or getattr(entity, "title", None)
        or str(getattr(entity, "id", "chat"))
    )
    label = sanitize_name(str(label))
    return base / label


async def fetch_album_messages(client: TelegramClient, entity, anchor_msg):
    if not anchor_msg.grouped_id:
        return [anchor_msg]

    min_id = max(anchor_msg.id - 50, 0)
    max_id = anchor_msg.id + 50
    candidates = [
        m
        async for m in client.iter_messages(
            entity,
            min_id=min_id,
            max_id=max_id,
        )
    ]
    grouped = [m for m in candidates if m and m.grouped_id == anchor_msg.grouped_id]
    if not grouped:
        return [anchor_msg]
    return sorted(grouped, key=lambda m: m.id)

async def fetch_topic_messages(client: TelegramClient, entity, top_msg_id: int):
    messages = [
        m async for m in client.iter_messages(entity, reply_to=top_msg_id)
    ]
    return sorted(messages, key=lambda m: m.id)


async def resolve_topic_title(client: TelegramClient, entity, message):
    reply_to = getattr(message, "reply_to", None)
    top_msg_id = None
    if reply_to:
        top_msg_id = (
            getattr(reply_to, "reply_to_top_id", None)
            or getattr(reply_to, "top_msg_id", None)
        )
        if not top_msg_id and getattr(reply_to, "forum_topic", False):
            top_msg_id = getattr(reply_to, "reply_to_msg_id", None)
    if not top_msg_id:
        top_msg_id = getattr(message, "topic_id", None)
    if not top_msg_id:
        return None
    topic_msg = await client.get_messages(entity, ids=top_msg_id)
    action = getattr(topic_msg, "action", None)
    title = getattr(action, "title", None)
    if title:
        return title
    # Fallback: if the topic message is plain text, use it as the title
    text = getattr(topic_msg, "message", None)
    return text


def get_topic_id_from_message(message):
    reply_to = getattr(message, "reply_to", None)
    top_msg_id = None
    if reply_to:
        top_msg_id = (
            getattr(reply_to, "reply_to_top_id", None)
            or getattr(reply_to, "top_msg_id", None)
        )
        if not top_msg_id and getattr(reply_to, "forum_topic", False):
            top_msg_id = getattr(reply_to, "reply_to_msg_id", None)
    if not top_msg_id:
        top_msg_id = getattr(message, "topic_id", None)
    return top_msg_id


async def main():
    banner_lines = [
        "        ░██                    ░███     ░███                                           ░██",
        "        ░██                    ░████   ░████                                           ░██",
        "        ░██          ░███████  ░██░██ ░██░██  ░██████   ░██░████  ░███████   ░███████  ░██",
        "        ░██         ░██    ░██ ░██ ░████ ░██       ░██  ░███     ░██    ░██ ░██    ░██ ░██",
        "        ░██         ░█████████ ░██  ░██  ░██  ░███████  ░██      ░██        ░█████████ ░██",
        "        ░██         ░██        ░██       ░██ ░██   ░██  ░██      ░██    ░██ ░██        ░██",
        "        ░██████████  ░███████  ░██       ░██  ░█████░██ ░██       ░███████   ░███████  ░██",
    ]
    # Simple blue -> green gradient per line (24-bit ANSI)
    start = (0, 120, 255)
    end = (0, 200, 120)
    total = max(len(banner_lines) - 1, 1)
    print("")
    for i, line in enumerate(banner_lines):
        t = i / total
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        print(f"\x1b[38;2;{r};{g};{b}m{line}\x1b[0m")
    print("")
    parser = argparse.ArgumentParser(
        description="Download Telegram photos/videos from a t.me message link"
    )
    parser.add_argument("link", nargs="?", help="Telegram message link")
    parser.add_argument(
        "--out",
        default=str(Path.home() / "Downloads" / "Telegram"),
        help="Output folder (default: ~/Downloads/Telegram)",
    )
    parser.add_argument(
        "--sms",
        action="store_true",
        help="Force SMS code delivery if possible",
    )
    parser.add_argument(
        "--qr",
        action="store_true",
        help="Login via QR code (recommended if code delivery fails)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info about the message and topic",
    )
    parser.add_argument(
        "--topic",
        action="store_true",
        help="Download all media from the topic (forum thread)",
    )
    parser.add_argument(
        "--menu",
        action="store_true",
        help="Interactive menu (message vs topic)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all media from the topic if available, otherwise from the channel/group",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of messages to scan (e.g. 500)",
    )
    parser.add_argument(
        "--only",
        choices=["photos", "videos"],
        help="Filter media (photos or videos only)",
    )
    parser.add_argument(
        "--skip-forwards",
        action="store_true",
        help="Skip forwarded messages",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable duplicate cache",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Disable JSONL download log",
    )
    parser.add_argument(
        "--reset-cache",
        action="store_true",
        help="Reset cache before running (optional)",
    )
    args = parser.parse_args()

    link = args.link
    if args.menu:
        print("Menu:")
        print("  1) Download media from the message")
        print("  2) Download all media (topic if available, otherwise channel/group)")
        choice = input("Choice (1/2): ").strip()
        if choice == "2":
            args.all = True
        link = input("Paste the Telegram message link: ").strip()
    if not link:
        link = input("Paste the Telegram message link: ").strip()

    parsed = parse_link(link)
    if not parsed:
        raise SystemExit("Invalid link. Example: https://t.me/channelname/123")

    load_dotenv()
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    session_name = os.getenv("TG_SESSION_NAME", "telegram")
    phone_env = os.getenv("TG_PHONE")

    if not api_id or not api_hash:
        raise SystemExit(
            "Missing variables. Set TG_API_ID and TG_API_HASH in a .env file."
        )

    try:
        api_id = int(api_id)
    except ValueError as exc:
        raise SystemExit("TG_API_ID must be an integer.") from exc

    client = TelegramClient(session_name, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            if args.qr:
                print("Open Telegram > Settings > Devices > Scan QR code.")
                qr_login = await client.qr_login()
                qr = qrcode.QRCode(border=1)
                qr.add_data(qr_login.url)
                qr.make(fit=True)
                qr.print_ascii(invert=True)
                await qr_login.wait()
            else:
                phone = sanitize_phone(phone_env) if phone_env else None
                if not phone:
                    phone = sanitize_phone(
                        input(
                    "Phone number in international format (e.g. +33612345678): "
                        ).strip()
                    )
                sent = await client.send_code_request(phone, force_sms=args.sms)
                code = input("Telegram login code: ").strip()
                try:
                    await client.sign_in(
                        phone=phone, code=code, phone_code_hash=sent.phone_code_hash
                    )
                except SessionPasswordNeededError:
                    password = getpass.getpass(
                        "Telegram password (2FA) if enabled: "
                    )
                    if not password:
                        raise SystemExit(
                            "2FA password required. Enable/disable 2FA in Telegram if needed."
                        )
                    await client.sign_in(password=password)

        # Load dialogs to help resolve t.me/c/... links
        await client.get_dialogs(limit=200)

        if parsed[0] == "username":
            _, username, msg_id = parsed
            entity = await client.get_entity(username)
        else:
            _, channel_id, msg_id = parsed
            entity = await client.get_entity(PeerChannel(channel_id))

        message = await client.get_messages(entity, ids=msg_id)
        if not message:
            raise SystemExit("Message not found or inaccessible.")

        if args.all:
            top_msg_id = get_topic_id_from_message(message)
            if top_msg_id:
                messages = await fetch_topic_messages(client, entity, top_msg_id)
            else:
                messages = [
                    m async for m in client.iter_messages(entity, limit=args.limit)
                ]
        elif args.topic:
            reply_to = getattr(message, "reply_to", None)
            top_msg_id = None
            if reply_to:
                top_msg_id = (
                    getattr(reply_to, "reply_to_top_id", None)
                    or getattr(reply_to, "top_msg_id", None)
                )
                if not top_msg_id and getattr(reply_to, "forum_topic", False):
                    top_msg_id = getattr(reply_to, "reply_to_msg_id", None)
            if not top_msg_id:
                top_msg_id = getattr(message, "topic_id", None)
            if not top_msg_id:
                raise SystemExit("This message does not seem to be in a topic.")
            messages = await fetch_topic_messages(client, entity, top_msg_id)
        else:
            messages = await fetch_album_messages(client, entity, message)
        media_messages = [m for m in messages if is_image_or_video_message(m)]
        if args.only:
            wanted = "image" if args.only == "photos" else "video"
            media_messages = [m for m in media_messages if media_kind(m) == wanted]
        if args.skip_forwards:
            media_messages = [
                m for m in media_messages if not getattr(m, "forward", None)
            ]

        if not media_messages:
            raise SystemExit("No photo or video found in this message.")

        output_base = Path(args.out)
        cache_path = output_base / "_cache" / "downloaded.json"
        if args.reset_cache and cache_path.exists():
            cache_path.unlink()
        cache = load_cache(cache_path) if not args.no_cache else {}
        log_path = None if args.no_log else (Path.cwd() / "_logs" / "downloads.jsonl")
        topic_title = await resolve_topic_title(client, entity, message)
        if args.debug:
            reply_to = getattr(message, "reply_to", None)
            print(f"Debug reply_to: {reply_to!r}")
            if reply_to and hasattr(reply_to, "to_dict"):
                print(f"Debug reply_to dict: {reply_to.to_dict()!r}")
            print(f"Debug message.topic_id: {getattr(message, 'topic_id', None)!r}")
            print(f"Debug topic_title: {topic_title!r}")
        if args.all and not topic_title:
            output_dir = build_channel_root(output_base, entity)
        else:
            output_dir = build_output_dir(output_base, entity, message.id, topic_title)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {len(media_messages)} file(s) to {output_dir}...")
        success = 0
        skipped = 0
        total_bytes = 0
        kind_counts = {"image": 0, "video": 0, "autre": 0}
        kind_bytes = {"image": 0, "video": 0, "autre": 0}
        for msg in tqdm(media_messages, desc="Downloading", unit="file"):
            cache_key = f"{entity.id}:{msg.id}"
            if not args.no_cache and cache.get(cache_key):
                skipped += 1
                log_event(
                    log_path,
                    {
                        "status": "skip",
                        "chat_id": entity.id,
                        "message_id": msg.id,
                        "reason": "cached",
                    },
                )
                continue
            path = await client.download_media(msg, file=output_dir)
            if path:
                success += 1
                kind = media_kind(msg)
                kind_counts[kind] += 1
                try:
                    size = Path(path).stat().st_size
                    total_bytes += size
                    kind_bytes[kind] += size
                except OSError:
                    pass
                if not args.no_cache:
                    cache[cache_key] = str(path)
                log_event(
                    log_path,
                    {
                        "status": "downloaded",
                        "chat_id": entity.id,
                        "message_id": msg.id,
                        "path": str(path),
                        "kind": kind,
                    },
                )

        total_mb = total_bytes / (1024 * 1024)
        print(
            f"Done. {success}/{len(media_messages)} downloaded, {total_mb:.2f} MB."
        )
        if skipped:
            print(f"Skipped: {skipped} already downloaded (cache).")
        print(
            f"Summary: {kind_counts['image']} photo(s), {kind_counts['video']} video(s), {kind_counts['autre']} other(s)."
        )
        print(
            "Size details: "
            f"photos {fmt_mb(kind_bytes['image'])}, "
            f"videos {fmt_mb(kind_bytes['video'])}, "
            f"others {fmt_mb(kind_bytes['autre'])}."
        )
        print("")
        print("Recap")
        print("Type   | #  | Size")
        print("image  | {:>2} | {}".format(kind_counts["image"], fmt_mb(kind_bytes["image"])))
        print("video  | {:>2} | {}".format(kind_counts["video"], fmt_mb(kind_bytes["video"])))
        print("other  | {:>2} | {}".format(kind_counts["autre"], fmt_mb(kind_bytes["autre"])))

        if not args.no_cache:
            save_cache(cache_path, cache)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
