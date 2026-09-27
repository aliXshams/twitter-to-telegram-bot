# Twitter-to-Telegram Bot

A Telegram bot that monitors Twitter for tweets matching a search query and forwards new ones to a Telegram channel. Tweets are fetched through [Nitter](https://github.com/zedeus/nitter)'s RSS feeds, so no Twitter API key is needed.

> **Status:** This repository is archived and no longer maintained. It depends on public Nitter instances, which are unreliable and frequently go offline.

## How it works

Every 15 minutes the bot polls a Nitter RSS search feed and forwards any tweets newer than the last check to the configured Telegram channel. The default query tracks `#cybersecurity` OR `#zeroday` from verified accounts, excluding replies and retweets. The target channel is chosen interactively via Telegram's channel picker.

## Requirements

- Python 3.8+
- A Telegram bot token (create one via [@BotFather](https://t.me/BotFather))
- A Telegram channel where the bot is an admin

## Installation

```shell
# Optional but recommended: use a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

On first run the script asks for three things and saves them to `config.py` (gitignored):

- **Telegram bot token** — from @BotFather
- **Admin ID** — your Telegram user ID; only admins can control the bot
- **Channel ID** — the target channel (can also be set later with `/add_channel`)

```shell
python main.py
```

The `query` variable and the Nitter instance URL are both set in `send_tweet()` inside `main.py` (see the live tracker at [status.d420.de](https://status.d420.de/) for working instances).

## Commands

| Command | Description |
| --- | --- |
| `/start` | Check the bot is running |
| `/add_channel` | Choose the target channel via Telegram's channel picker (replaces any existing one) |
| `/channel_start` | Start forwarding new tweets (checks every 15 minutes) |
| `/channel_stop` | Stop forwarding |

All commands are admin-only; other users get an "Unauthorized User!" reply.

## Known limitations

- Depends on a public Nitter instance (currently `nitter.privacydev.net`, hardcoded in `main.py`). Nitter instances are unreliable and many have shut down. If a fetch fails, the bot logs the error and skips that cycle.
- The search query is hardcoded; it can't be changed at runtime.

## License

MIT, see [LICENSE](LICENSE).
