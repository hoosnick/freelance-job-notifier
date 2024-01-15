from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def apply_button(text: str, url: str, data: dict | None = None, in_group: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, url=url))

    if data is not None:
        what_to_offer = "Что предложить?" if data['lang'] == 'ru' else "What to offer?"
        more_info = "Доп. инфо" if data['lang'] == 'ru' else "More details"

        if in_group:
            builder.add(
                InlineKeyboardButton(
                    text=what_to_offer,
                    url=f"https://t.me/{data['username']}?start=project_{data['id']}"
                )
            )
        else:
            builder.add(InlineKeyboardButton(
                text=more_info, url=data['group_link']
            ))
            builder.add(
                InlineKeyboardButton(
                    text=what_to_offer,
                    web_app=WebAppInfo(
                        url=f"{data['url']}?project={data['id']}&lang={data['lang']}"
                    )
                )
            )

    return builder.adjust(2).as_markup()
