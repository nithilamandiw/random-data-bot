# Random Data Telegram Bot

A Python Telegram bot for generating country-based random test data.

The bot can generate:

- Names
- Addresses
- Phone numbers with country calling codes
- Mexico neighborhoods
- USA random SSNs
- EU random IBANs

This project is intended for testing forms, demos, QA workflows, and development data.

## Features

- Generate data by command:

```text
/random us
/name lk
/iban de
```

- Or use the Telegram menu:

```text
Address | Name | IBAN
```

After selecting a mode, send only a country code:

```text
us
lk
mx
fr
de
```

- Copy buttons for generated fields:

```text
Copy Name
Copy Street
Copy Phone
Copy Country
Copy Random IBAN
```

- Regenerate buttons for addresses and IBANs.
- Monospace values for easier reading and copying.
- Valid ISO 2-letter country codes are accepted.
- Friendly aliases like `uk`, `usa`, and `sri_lanka` are supported.

## Commands

```text
/start
/help
/random <country_code>
/name <country_code>
/iban <eu_country_code>
```

Examples:

```text
/random lk
/random mx
/random us
/name jp
/iban de
/iban fr
```

## Country Behavior

The bot accepts real ISO 2-letter country codes:

```text
lk = Sri Lanka
us = United States
mx = Mexico
gb = United Kingdom
de = Germany
fr = France
```

For countries with curated data, city/state/postal-code combinations are kept together.

Currently curated address data includes:

```text
lk, mx, us, gb, de, fr
```

Other valid countries still work, but they may use a random fallback address style when exact local address data is unavailable.

## Phone Numbers

Phone numbers are normalized to compact international format:

```text
+<country_calling_code><number>
```

Examples:

```text
+94789963770
+525587546710
+33261547812
```

The bot removes spaces, dashes, brackets, and extensions.

## USA Random SSN

For `us`, the bot includes a random SSN:

```text
- SSN (Random): 943-56-7208
```

These are generated in an invalid/reserved range and are only for testing.

## EU Random IBAN

Use:

```text
/iban de
/iban fr
/iban nl
```

Example:

```text
Germany Random IBAN
------------------------------
- IBAN (Random): DE21773023468935511493
- Country: Germany
------------------------------
```

IBAN output has no spaces and includes a copy button.

## Download

Clone the repository:

```bash
git clone https://github.com/nithilamandiw/random-data-bot.git
cd random-data-bot
```

Or download it from GitHub:

```text
Code -> Download ZIP
```

## Setup

Create a Telegram bot with `@BotFather`, then copy the bot token.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Put your real bot token inside `.env`:

```text
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Run the bot:

```bash
python -m random_name_bot.bot
```

## Test

```bash
python -m unittest discover
```

## Requirements

- Python 3.9+
- Telegram bot token from `@BotFather`

Python packages:

- `python-telegram-bot`
- `Faker`
- `pycountry`
- `phonenumbers`

## Safety

All generated data is random and intended for testing. Do not use it for fraud, impersonation, banking, identity verification, or any real account ownership claim.
