from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from utils.categories import EXPENSE_CATEGORIES


def expense_categories_keyboard():

    buttons = []

    for category in EXPENSE_CATEGORIES:

        buttons.append([
            InlineKeyboardButton(
                text=category,
                callback_data=f"category_{category}"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )