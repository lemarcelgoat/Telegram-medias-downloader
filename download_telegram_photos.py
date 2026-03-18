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
    r"(?:(?P<username>[A-Za-z0-9_]+)/(?P<msgid>\d+)(?:/(?P<msgid2>\d+))?"
    r"|c/(?P<cid>\d+)/(?P<cmsgid>\d+)(?:/(?P<cmsgid2>\d+))?)",
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
    return f"{value / (1024 * 1024):.2f} Mo"


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
    # Fallback: if the topic message is plain text, use it as title
    text = getattr(topic_msg, "message", None)
    return text


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
        description="Telecharge les photos d'un message Telegram a partir d'un lien t.me"
    )
    parser.add_argument("link", nargs="?", help="Lien du message Telegram")
    parser.add_argument(
        "--out",
        default=str(Path.home() / "Downloads" / "Telegram"),
        help="Dossier de sortie (defaut: ~/Downloads/Telegram)",
    )
    parser.add_argument(
        "--sms",
        action="store_true",
        help="Force l'envoi du code par SMS si possible",
    )
    parser.add_argument(
        "--qr",
        action="store_true",
        help="Connexion via QR code (recommande si l'envoi du code ne marche pas)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Affiche des infos de debug sur le message et le sujet",
    )
    parser.add_argument(
        "--topic",
        action="store_true",
        help="Telecharge tous les medias du sujet (topic) du message",
    )
    parser.add_argument(
        "--menu",
        action="store_true",
        help="Menu interactif (choix entre message ou sujet)",
    )
    parser.add_argument(
        "--only",
        choices=["photos", "videos"],
        help="Filtre les medias (photos ou videos uniquement)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Desactive le cache anti-doublons",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Desactive le journal JSONL des telechargements",
    )
    parser.add_argument(
        "--reset-cache",
        action="store_true",
        help="Supprime le cache avant de lancer (optionnel)",
    )
    args = parser.parse_args()

    link = args.link
    if args.menu:
        print("Menu:")
        print("  1) Telecharger medias du message")
        print("  2) Telecharger tous les medias du sujet (topic)")
        choice = input("Choix (1/2): ").strip()
        if choice == "2":
            args.topic = True
        link = input("Colle le lien du message Telegram: ").strip()
    if not link:
        link = input("Colle le lien du message Telegram: ").strip()

    parsed = parse_link(link)
    if not parsed:
        raise SystemExit("Lien invalide. Exemple attendu: https://t.me/nomduchannel/123")

    load_dotenv()
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    session_name = os.getenv("TG_SESSION_NAME", "telegram")
    phone_env = os.getenv("TG_PHONE")

    if not api_id or not api_hash:
        raise SystemExit(
            "Variables manquantes. Renseigne TG_API_ID et TG_API_HASH dans un fichier .env."
        )

    try:
        api_id = int(api_id)
    except ValueError as exc:
        raise SystemExit("TG_API_ID doit etre un entier.") from exc

    client = TelegramClient(session_name, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            if args.qr:
                print("Ouvre Telegram > Parametres > Appareils > Scanner un QR code.")
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
                            "Numero de telephone au format international (ex: +33612345678): "
                        ).strip()
                    )
                sent = await client.send_code_request(phone, force_sms=args.sms)
                code = input("Code de connexion Telegram: ").strip()
                try:
                    await client.sign_in(
                        phone=phone, code=code, phone_code_hash=sent.phone_code_hash
                    )
                except SessionPasswordNeededError:
                    password = getpass.getpass(
                        "Mot de passe Telegram (2FA) si active: "
                    )
                    await client.sign_in(password=password)

        # Charge les dialogues pour faciliter la resolution des liens t.me/c/...
        await client.get_dialogs(limit=200)

        if parsed[0] == "username":
            _, username, msg_id = parsed
            entity = await client.get_entity(username)
        else:
            _, channel_id, msg_id = parsed
            entity = await client.get_entity(PeerChannel(channel_id))

        message = await client.get_messages(entity, ids=msg_id)
        if not message:
            raise SystemExit("Message introuvable ou inaccessible.")

        if args.topic:
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
                raise SystemExit("Ce message ne semble pas etre dans un sujet (topic).")
            messages = await fetch_topic_messages(client, entity, top_msg_id)
        else:
            messages = await fetch_album_messages(client, entity, message)
        media_messages = [m for m in messages if is_image_or_video_message(m)]
        if args.only:
            wanted = "image" if args.only == "photos" else "video"
            media_messages = [m for m in media_messages if media_kind(m) == wanted]

        if not media_messages:
            raise SystemExit("Aucune photo ou video trouvee dans ce message.")

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
        output_dir = build_output_dir(output_base, entity, message.id, topic_title)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Telechargement de {len(media_messages)} fichier(s) vers {output_dir}...")
        success = 0
        total_bytes = 0
        kind_counts = {"image": 0, "video": 0, "autre": 0}
        kind_bytes = {"image": 0, "video": 0, "autre": 0}
        for msg in tqdm(media_messages, desc="Telechargement", unit="fichier"):
            cache_key = f"{entity.id}:{msg.id}"
            if not args.no_cache and cache.get(cache_key):
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
            f"Termine. {success}/{len(media_messages)} telecharge(s), {total_mb:.2f} Mo."
        )
        print(
            f"Resume: {kind_counts['image']} photo(s), {kind_counts['video']} video(s), {kind_counts['autre']} autre(s)."
        )
        print(
            "Details tailles: "
            f"photos {fmt_mb(kind_bytes['image'])}, "
            f"videos {fmt_mb(kind_bytes['video'])}, "
            f"autres {fmt_mb(kind_bytes['autre'])}."
        )
        print("")
        print("Recapitulatif")
        print("Type   | Nb | Taille")
        print("image  | {:>2} | {}".format(kind_counts["image"], fmt_mb(kind_bytes["image"])))
        print("video  | {:>2} | {}".format(kind_counts["video"], fmt_mb(kind_bytes["video"])))
        print("autre  | {:>2} | {}".format(kind_counts["autre"], fmt_mb(kind_bytes["autre"])))

        if not args.no_cache:
            save_cache(cache_path, cache)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
