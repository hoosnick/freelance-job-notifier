from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def apply_button(
    text: str,
    url: str,
    data: dict | None = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, url=url))

    what2offer = {
        "ru": "Что предложить?",
        "en": "What to offer?"
    }

    if data is not None:
        builder.add(
            InlineKeyboardButton(
                text=what2offer[data.get("lang", "en")],
                url="https://t.me/{username}/app?startapp={id}_{lang}"
                .format(**data)
            )
        )

    return builder.adjust(2).as_markup()
