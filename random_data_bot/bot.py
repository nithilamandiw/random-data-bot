from __future__ import annotations

import logging
import os
from html import escape
from pathlib import Path

from telegram import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from random_data_bot.country_names import (
    format_fake_address,
    format_fake_iban,
    generate_fake_address,
    generate_fake_iban,
    generate_name,
    monospace,
    normalize_country_code,
    resolve_country,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


HELP_TEXT = """Use /name <country_code> to generate a random name.
Use /random <country_code> to generate a random address.
Use /iban <country_code> to generate a random EU IBAN.
Or select Address, Name, or IBAN, then send only a country code.

Examples:
/name lk
/name us
/name gb
/name jp
/random lk
/random gb
/iban de
/iban fr
lk
us

Country codes use ISO 2-letter codes. Aliases like /name uk and /name usa also work."""

MODE_ADDRESS = "address"
MODE_NAME = "name"
MODE_IBAN = "iban"

INVALID_COUNTRY_TEXT = "Invalid country code. Use a real 2-letter code like lk, us, gb, jp, or fr."
UNSUPPORTED_IBAN_TEXT = "IBAN generation is available for EU country codes like de, fr, nl, es, or it."

MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Address"), KeyboardButton("Name"), KeyboardButton("IBAN")],
    ],
    resize_keyboard=True,
)


def load_env_file() -> None:
    env_file = Path(".env")
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = MODE_ADDRESS
    await update.message.reply_text(
        f"Welcome to Random Data Bot.\n\n{HELP_TEXT}\n\nSelected: Address",
        reply_markup=MENU_KEYBOARD,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, reply_markup=MENU_KEYBOARD)


async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please add a country code.\n\nExamples:\n/name lk\n/name us\n/name jp"
        )
        return

    country_code = context.args[0]

    await send_name(update, country_code)


async def fake_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please add a country code.\n\nExamples:\n/random lk\n/random us\n/random gb"
        )
        return

    await send_fake_address(update, context.args[0])


async def iban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please add an EU country code.\n\nExamples:\n/iban de\n/iban fr\n/iban nl"
        )
        return

    await send_fake_iban(update, context.args[0])


async def regenerate_fake_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    country_code = query.data.removeprefix("fake:")

    try:
        message_text, keyboard = build_fake_address_response(country_code)
    except ValueError:
        await query.edit_message_text(INVALID_COUNTRY_TEXT)
        return

    await query.edit_message_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def regenerate_fake_iban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    country_code = query.data.removeprefix("iban:")

    try:
        message_text, keyboard = build_fake_iban_response(country_code)
    except ValueError:
        await query.edit_message_text(UNSUPPORTED_IBAN_TEXT)
        return

    await query.edit_message_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def send_fake_address(update: Update, country_code: str) -> None:
    try:
        message_text, keyboard = build_fake_address_response(country_code)
    except ValueError:
        await update.message.reply_text(INVALID_COUNTRY_TEXT)
        return

    await update.message.reply_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def send_fake_iban(update: Update, country_code: str) -> None:
    try:
        message_text, keyboard = build_fake_iban_response(country_code)
    except ValueError:
        await update.message.reply_text(UNSUPPORTED_IBAN_TEXT)
        return

    await update.message.reply_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def country_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.strip()

    selected_mode = parse_mode_selection(message_text)
    if selected_mode:
        context.user_data["mode"] = selected_mode
        await update.message.reply_text(
            f"Selected: {selected_mode.title()}\nNow send a country code like lk, us, mx, de, or fr.",
            reply_markup=MENU_KEYBOARD,
        )
        return

    if len(message_text.split()) != 1:
        return

    try:
        country = resolve_country(message_text)
    except ValueError:
        await update.message.reply_text(
            "Send a country code like lk, us, mx, gb, de, or fr."
        )
        return

    mode = context.user_data.get("mode", MODE_ADDRESS)

    if mode == MODE_NAME:
        await send_name(update, country.code)
    elif mode == MODE_IBAN:
        await send_fake_iban(update, country.code)
    else:
        await send_fake_address(update, country.code)


async def send_name(update: Update, country_code: str) -> None:
    try:
        message_text, keyboard = build_name_response(country_code)
    except ValueError:
        await update.message.reply_text(
            INVALID_COUNTRY_TEXT,
            reply_markup=MENU_KEYBOARD,
        )
        return

    await update.message.reply_text(
        message_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


def parse_mode_selection(message_text: str) -> str | None:
    normalized = message_text.strip().lower()
    if normalized in {"address", "random", "addr"}:
        return MODE_ADDRESS
    if normalized in {"name", "names"}:
        return MODE_NAME
    if normalized in {"iban", "bank"}:
        return MODE_IBAN

    return None


def build_fake_address_response(country_code: str) -> tuple[str, InlineKeyboardMarkup]:
    fake_address = generate_fake_address(country_code)
    code = normalize_country_code(country_code).lower()
    keyboard = build_fake_address_keyboard(fake_address, code)
    return format_fake_address(fake_address), keyboard


def build_name_response(country_code: str) -> tuple[str, InlineKeyboardMarkup]:
    full_name, country = generate_name(country_code)
    fallback_note = ""
    if country.uses_fallback:
        fallback_note = "\n\nNo exact name style is available yet, so I used a global style."

    message_text = (
        f"{monospace(full_name)}\n\n"
        f"Country: {escape(country.name)} ({country.code.lower()}){fallback_note}"
    )
    keyboard = InlineKeyboardMarkup([[copy_button("Copy Name", full_name)]])
    return message_text, keyboard


def build_fake_iban_response(country_code: str) -> tuple[str, InlineKeyboardMarkup]:
    fake_iban = generate_fake_iban(country_code)
    code = normalize_country_code(country_code).lower()
    keyboard = InlineKeyboardMarkup(
        [
            [copy_button("Copy Random IBAN", fake_iban.iban)],
            [InlineKeyboardButton("Regenerate IBAN", callback_data=f"iban:{code}")],
        ]
    )
    return format_fake_iban(fake_iban), keyboard


def build_fake_address_keyboard(fake_address, country_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Regenerate", callback_data=f"fake:{country_code}")]]
    )


def copy_button(label: str, value: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, copy_text=CopyTextButton(value))


def main() -> None:
    load_env_file()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN before running the bot.")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("name", name_command))
    app.add_handler(CommandHandler("random", fake_command))
    app.add_handler(CommandHandler("fake", fake_command))
    app.add_handler(CommandHandler("iban", iban_command))
    app.add_handler(CallbackQueryHandler(regenerate_fake_address, pattern=r"^fake:"))
    app.add_handler(CallbackQueryHandler(regenerate_fake_iban, pattern=r"^iban:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, country_code_message))

    app.run_polling()


if __name__ == "__main__":
    main()
