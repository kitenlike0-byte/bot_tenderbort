from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💳 Баланс"),
            KeyboardButton(text="📊 Статистика")
        ],
        [
            KeyboardButton(text="➕ Доход"),
            KeyboardButton(text="➖ Расход")
        ]
    ],
    resize_keyboard=True
)