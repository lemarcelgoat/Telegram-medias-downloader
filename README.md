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

### Full channel/group

To download all media from a channel or group:

```bash
python download_telegram_photos.py "https://t.me/channelname/123" --all
```

Limit the scan:

```bash
python download_telegram_photos.py "https://t.me/channelname/123" --all --limit 500
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
2. Renseigne `TG_API_ID` et `TG_API_HASH` depuis https://my.telegram.org.

Au premier lancement, Telethon te demandera ton numéro de téléphone et le code de connexion.

### Utilisation

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123"
```

Ou sans argument, le script te demandera le lien.
Si l’envoi de code ne marche pas, utilise la connexion QR :

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

### UX : barre de progression + résumé

Le script affiche une barre `tqdm` et un résumé par type et taille.

### Cache (éviter les doublons)

Le cache est **actif par défaut**.
Un cache JSON est stocké dans `~/Downloads/Telegram/_cache/downloaded.json`.
Pour le désactiver :

```bash
python download_telegram_photos.py "https://t.me/..." --no-cache
```

Pour repartir de zéro :

```bash
python download_telegram_photos.py "https://t.me/..." --reset-cache
```

### Log JSONL

Le journal est **actif par défaut** et stocké dans `_logs/downloads.jsonl` (à côté du script).
Pour le désactiver :

```bash
python download_telegram_photos.py "https://t.me/..." --no-log
```

### Sujet (topic) complet

Pour télécharger tous les médias d’un sujet (forum) :

```bash
python download_telegram_photos.py "https://t.me/nomdugroupe/123/456" --topic
```

### Canal/groupe complet

Pour télécharger tous les médias d’un canal ou groupe :

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123" --all
```

Limiter le scan :

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123" --all --limit 500
```

### Menu interactif

```bash
python download_telegram_photos.py --menu
```

Les médias sont téléchargés dans `~/Downloads/Telegram/<channel>/<message_id>/`.
Dans un groupe avec sujets (forum), le dossier prend le nom du sujet quand il est détecté.

### Types de liens supportés

- `https://t.me/nomduchannel/123`
- `https://t.me/c/123456/789` (channels/groupes privés ou non publics)

### Notes

- Le script utilise ton compte Telegram (pas de bot).
- Il télécharge les images et les vidéos.
- Il fonctionne seulement si tu as accès au message.
