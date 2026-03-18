# Telegram Media Downloader

[EN](#english) | [FR](#français)

## English

Small Python script to download photos and videos from a Telegram message (including albums) using a t.me link.

### Installation

1. Create a Python environment (optional but recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`.
2. Create an app on https://my.telegram.org (API Development Tools).
3. Fill `TG_API_ID` and `TG_API_HASH` from that page.

At first run, Telethon will ask for your phone number and the login code.

### Usage

```bash
python download_telegram_photos.py "https://t.me/channelname/123"
```

If you don't receive the code, use QR login:

```bash
python download_telegram_photos.py "https://t.me/channelname/123" --qr
```

### Quick memo

```bash
# Full help
python download_telegram_photos.py --help

# Interactive menu
python download_telegram_photos.py --menu

# Full topic (forum)
python download_telegram_photos.py "https://t.me/groupname/123/456" --topic

# Full channel/group
python download_telegram_photos.py "https://t.me/channelname/123" --all

# Full channel/group (limit scan)
python download_telegram_photos.py "https://t.me/channelname/123" --all --limit 500

# QR login
python download_telegram_photos.py "https://t.me/..." --qr

# Cache (enabled by default)
python download_telegram_photos.py "https://t.me/..."

# Disable cache
python download_telegram_photos.py "https://t.me/..." --no-cache

# Reset cache
python download_telegram_photos.py "https://t.me/..." --reset-cache

# Logs (enabled by default)
python download_telegram_photos.py "https://t.me/..."

# Disable logs
python download_telegram_photos.py "https://t.me/..." --no-log

# Filter photos or videos
python download_telegram_photos.py "https://t.me/..." --only photos
python download_telegram_photos.py "https://t.me/..." --only videos

# Skip forwarded messages
python download_telegram_photos.py "https://t.me/..." --skip-forwards
```

### Notes

- The script uses your Telegram account (no bot).
- It downloads images and videos.
- It only works if you can access the message.

### Troubleshooting

- **No code received**: use `--qr` to login by scanning a QR code.
- **Message not found**: make sure the link is correct and you have access to the chat.
- **No media found**: the message may not contain photos/videos, or the link points to the wrong message.

## Français

Petit script Python pour télécharger les photos et vidéos d’un message Telegram (y compris les albums) à partir d’un lien t.me.

### Installation

1. Crée un environnement Python (optionnel mais recommandé).
2. Installe les dépendances :

```bash
pip install -r requirements.txt
```

### Configuration

1. Copie `.env.example` vers `.env`.
2. Crée une app sur https://my.telegram.org (API Development Tools).
3. Renseigne `TG_API_ID` et `TG_API_HASH` depuis cette page.

Au premier lancement, Telethon te demandera ton numéro de téléphone et le code de connexion.

### Utilisation

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123"
```

Ou sans argument, le script te demandera le lien.
Si tu ne reçois pas le code, utilise la connexion QR :

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123" --qr
```

Le script affiche un QR directement dans le terminal. Il suffit de le scanner avec Telegram.

### Mémo rapide

```bash
# Aide complète
python download_telegram_photos.py --help

# Menu interactif
python download_telegram_photos.py --menu

# Tout le sujet (topic)
python download_telegram_photos.py "https://t.me/nomdugroupe/123/456" --topic

# Tout le canal/groupe
python download_telegram_photos.py "https://t.me/nomduchannel/123" --all

# Tout le canal/groupe (limite)
python download_telegram_photos.py "https://t.me/nomduchannel/123" --all --limit 500

# Connexion par QR
python download_telegram_photos.py "https://t.me/..." --qr

# Cache anti-doublons (actif par défaut)
python download_telegram_photos.py "https://t.me/..."

# Désactiver le cache
python download_telegram_photos.py "https://t.me/..." --no-cache

# Reset cache (optionnel)
python download_telegram_photos.py "https://t.me/..." --reset-cache

# Log JSONL (actif par défaut)
python download_telegram_photos.py "https://t.me/..."

# Désactiver le log
python download_telegram_photos.py "https://t.me/..." --no-log

# Filtrer photos ou vidéos
python download_telegram_photos.py "https://t.me/..." --only photos
python download_telegram_photos.py "https://t.me/..." --only videos

# Ignorer les messages transférés
python download_telegram_photos.py "https://t.me/..." --skip-forwards
```

### Notes

- Le script utilise ton compte Telegram (pas de bot).
- Il télécharge les images et les vidéos.
- Il fonctionne seulement si tu as accès au message.

### Dépannage

- **Code non reçu** : utilise `--qr` pour te connecter via QR code.
- **Message introuvable** : vérifie le lien et tes accès au chat.
- **Aucun média trouvé** : le message ne contient peut-être pas de photos/vidéos, ou le lien pointe vers un autre message.
