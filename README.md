# Telegram Media Downloader

[EN](#english) | [FR](#francais)

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
2. Fill `TG_API_ID` and `TG_API_HASH` from https://my.telegram.org.

At first run, Telethon will ask for your phone number and the login code.

### Usage

```bash
python download_telegram_photos.py "https://t.me/channelname/123"
```

If code delivery does not work, use QR login:

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
```

### UX: progress + summary

The script shows a `tqdm` progress bar and a summary by type and size.

### Cache (avoid duplicates)

Cache is enabled by default.
Stored in `~/Downloads/Telegram/_cache/downloaded.json`.
Disable with:

```bash
python download_telegram_photos.py "https://t.me/..." --no-cache
```

### Logs

Logs are enabled by default and stored in `_logs/downloads.jsonl` (next to the script).
Disable with:

```bash
python download_telegram_photos.py "https://t.me/..." --no-log
```

### Full topic

To download all media from a forum topic:

```bash
python download_telegram_photos.py "https://t.me/groupname/123/456" --topic
```

### Interactive menu

```bash
python download_telegram_photos.py --menu
```

Media are saved to `~/Downloads/Telegram/<channel>/<message_id>/`.
In forum groups, the folder uses the topic name when available.

### Supported links

- `https://t.me/channelname/123`
- `https://t.me/c/123456/789` (private/non-public channels or groups)

### Notes

- The script uses your Telegram account (no bot).
- It downloads images and videos.
- It only works if you can access the message.

## Francais

Petit script Python pour telecharger les photos et videos d'un message Telegram (y compris les albums) a partir d'un lien t.me.

### Installation

1. Cree un environnement Python (optionnel mais recommande).
2. Installe les dependances:

```bash
pip install -r requirements.txt
```

### Configuration

1. Copie `.env.example` vers `.env`.
2. Renseigne `TG_API_ID` et `TG_API_HASH` depuis https://my.telegram.org.

Au premier lancement, Telethon te demandera ton numero de telephone et le code de connexion.

### Utilisation

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123"
```

Ou sans argument, le script te demandera le lien.
Si l'envoi de code ne marche pas, utilise la connexion QR:

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123" --qr
```

Le script affiche un QR directement dans le terminal. Il suffit de le scanner avec Telegram.

### Memo rapide

```bash
# Aide complete
python download_telegram_photos.py --help

# Menu interactif
python download_telegram_photos.py --menu

# Tout le sujet (topic)
python download_telegram_photos.py "https://t.me/nomdugroupe/123/456" --topic

# Connexion par QR
python download_telegram_photos.py "https://t.me/..." --qr

# Cache anti-doublons (actif par defaut)
python download_telegram_photos.py "https://t.me/..."

# Desactiver le cache
python download_telegram_photos.py "https://t.me/..." --no-cache

# Reset cache (optionnel)
python download_telegram_photos.py "https://t.me/..." --reset-cache

# Log JSONL (actif par defaut)
python download_telegram_photos.py "https://t.me/..."

# Desactiver le log
python download_telegram_photos.py "https://t.me/..." --no-log

# Filtrer photos ou videos
python download_telegram_photos.py "https://t.me/..." --only photos
python download_telegram_photos.py "https://t.me/..." --only videos
```

### UX: barre de progression + resume

Le script affiche une barre `tqdm` et un resume par type et taille.

### Cache (eviter les doublons)

Le cache est **actif par defaut**.
Un cache JSON est stocke dans `~/Downloads/Telegram/_cache/downloaded.json`.
Pour le desactiver:

```bash
python download_telegram_photos.py "https://t.me/..." --no-cache
```

Pour repartir de zero:

```bash
python download_telegram_photos.py "https://t.me/..." --reset-cache
```

### Log JSONL

Le journal est **actif par defaut** et stocke dans `_logs/downloads.jsonl` (a cote du script).
Pour le desactiver:

```bash
python download_telegram_photos.py "https://t.me/..." --no-log
```

### Sujet (topic) complet

Pour telecharger tous les medias d'un sujet (forum):

```bash
python download_telegram_photos.py "https://t.me/nomdugroupe/123/456" --topic
```

### Menu interactif

```bash
python download_telegram_photos.py --menu
```

Les medias sont telecharges dans `~/Downloads/Telegram/<channel>/<message_id>/`.
Dans un groupe avec sujets (forum), le dossier prend le nom du sujet quand il est detecte.

### Types de liens supportes

- `https://t.me/nomduchannel/123`
- `https://t.me/c/123456/789` (channels/groupes prives ou non publics)

### Notes

- Le script utilise ton compte Telegram (pas de bot).
- Il telecharge les images et les videos.
- Il fonctionne seulement si tu as acces au message.