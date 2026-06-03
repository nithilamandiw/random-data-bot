# Random Name Telegram Bot

A Python Telegram bot that generates random names by country code.

## Commands

```text
/start
/help
/name <country_code>
/fake <country_code>
```

Examples:

```text
/name lk
/name us
/name gb
/name jp
/fake lk
/fake us
```

`/fake <country_code>` returns a random fake address with a name, street, city,
state, postal code, and country. The message includes a `Regenerate` button that
creates another address for the same country.

The bot accepts real ISO 2-letter country codes. Some friendly aliases also work:

```text
/name uk  -> United Kingdom
/name usa -> United States
```

For countries where Faker has an exact locale, the bot uses that locale. For other valid countries, it accepts the country code and falls back to a global/default name style.

## Setup

Create a bot with Telegram `@BotFather`, then copy the token.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Then put your real bot token inside `.env`.

Run the bot:

```bash
python -m random_name_bot.bot
```

## Test

```bash
python -m unittest discover
```
