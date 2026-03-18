# Telegram Photo Downloader (perso)

Petit script Python pour telecharger les photos et videos d'un message Telegram (y compris les albums) a partir d'un lien t.me.

## Installation

1. Cree un environnement Python (optionnel mais recommande).
2. Installe les dependances:

```bash
pip install -r requirements.txt
```

## Configuration

1. Copie `.env.example` vers `.env`.
2. Renseigne `TG_API_ID` et `TG_API_HASH` depuis https://my.telegram.org.

Au premier lancement, Telethon te demandera ton numero de telephone et le code de connexion.

## Utilisation

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123"
```

Ou sans argument, le script te demandera le lien.
Si l'envoi de code ne marche pas, utilise la connexion QR:

```bash
python download_telegram_photos.py "https://t.me/nomduchannel/123" --qr
```

Le script affiche un QR directement dans le terminal. Il suffit de le scanner avec Telegram.

## Memo rapide

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
python download_telegram_photos.py "https://t.me/..." --cache --reset-cache

# Log JSONL (actif par defaut)
python download_telegram_photos.py "https://t.me/..."

# Desactiver le log
python download_telegram_photos.py "https://t.me/..." --no-log

# Filtrer photos ou videos
python download_telegram_photos.py "https://t.me/..." --only photos
python download_telegram_photos.py "https://t.me/..." --only videos
```

## UX: barre de progression + resume

Le script affiche une barre `tqdm` et un resume par type et taille.

## Cache (eviter les doublons)

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

## Log JSONL

Le journal est **actif par defaut** et stocke dans `_logs/downloads.jsonl` (a cote du script).
Pour le desactiver:

```bash
python download_telegram_photos.py "https://t.me/..." --no-log
```

## Sujet (topic) complet

Pour telecharger tous les medias d'un sujet (forum):

```bash
python download_telegram_photos.py "https://t.me/nomdugroupe/123/456" --topic
```

## Menu interactif

```bash
python download_telegram_photos.py --menu
```

Les medias sont telecharges dans `~/Downloads/Telegram/<channel>/<message_id>/`.
Dans un groupe avec sujets (forum), le dossier prend le nom du sujet quand il est detecte.

## Types de liens supportes

- `https://t.me/nomduchannel/123`
- `https://t.me/c/123456/789` (channels/groupes prives ou non publics)

## Notes

- Le script utilise ton compte Telegram (pas de bot).
- Il telecharge les images et les videos.
- Il fonctionne seulement si tu as acces au message.
