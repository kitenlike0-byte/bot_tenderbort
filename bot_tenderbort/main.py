import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID
from db import (
    init_db,
    add_transaction,
    get_balance,
    get_stats,
    get_last_transactions,
    get_category_stats
)
from keyboards.main_menu import main_menu
from utils.categories import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES
)
from utils.parser import parse_transaction


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==========================
# FSM
# ==========================

class TransactionFSM(StatesGroup):
    type = State()
    amount = State()
    category = State()
    description = State()


class ComplaintFSM(StatesGroup):
    text = State()


# ==========================
# START
# ==========================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в финансового бота!\n\n"
        "Записывай доходы и расходы прямо сообщением.\n\n"
        "Примеры:\n"
        "-500 еда\n"
        "+2000 зарплата",
        reply_markup=main_menu
    )


# ==========================
# BALANCE
# ==========================

@dp.message(Command("balance"))
@dp.message(F.text == "💳 Баланс")
async def balance(message: types.Message):
    user_id = message.from_user.id
    balance_value = get_balance(user_id)

    await message.answer(
        f"💳 Твой баланс: <b>{balance_value:.2f} ₽</b>",
        parse_mode="HTML"
    )


# ==========================
# STATS
# ==========================

@dp.message(Command("stats"))
@dp.message(F.text == "📊 Статистика")
async def stats(message: types.Message):
    user_id = message.from_user.id

    stats_data = get_stats(user_id)
    transactions = get_last_transactions(user_id)
    category_stats = get_category_stats(user_id)

    text = (
        "📊 <b>Финансовая статистика</b>\n\n"
        f"💰 Баланс: <b>{stats_data['balance']:.2f} ₽</b>\n"
        f"📈 Доходы: <b>+{stats_data['income']:.2f} ₽</b>\n"
        f"📉 Расходы: <b>-{stats_data['expense']:.2f} ₽</b>\n\n"
    )

    # Категории
    if category_stats:
        text += "📂 <b>Категории расходов:</b>\n"

        for category, amount in category_stats:
            text += f"• {category}: {amount:.2f} ₽\n"

        text += "\n"

    # Последние операции
    text += "🕒 <b>Последние операции:</b>\n"

    if not transactions:
        text += "Нет операций."
    else:
        for amount, tx_type, category in transactions:
            emoji = "💰" if tx_type == "income" else "💸"
            text += f"{emoji} {amount:.2f} ₽ | {category}\n"

    await message.answer(
        text,
        parse_mode="HTML"
    )


# ==========================
# ДОХОД
# ==========================

@dp.message(F.text == "➕ Доход")
async def income_start(message: types.Message, state: FSMContext):
    await state.set_state(TransactionFSM.amount)
    await state.update_data(type="income")

    await message.answer(
        "💰 Введите сумму дохода:"
    )


# ==========================
# РАСХОД
# ==========================

@dp.message(F.text == "➖ Расход")
async def expense_start(message: types.Message, state: FSMContext):
    await state.set_state(TransactionFSM.amount)
    await state.update_data(type="expense")

    await message.answer(
        "💸 Введите сумму расхода:"
    )


# ==========================
# СУММА
# ==========================

@dp.message(TransactionFSM.amount)
async def get_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return

    await state.update_data(amount=amount)

    data = await state.get_data()

    categories = (
        INCOME_CATEGORIES
        if data["type"] == "income"
        else EXPENSE_CATEGORIES
    )

    text = "📂 Выберите категорию:\n\n"
    text += "\n".join(categories)

    await state.set_state(TransactionFSM.category)
    await message.answer(text)


# ==========================
# КАТЕГОРИЯ
# ==========================

@dp.message(TransactionFSM.category)
async def get_category(message: types.Message, state: FSMContext):
    await state.update_data(
        category=message.text.lower()
    )

    await state.set_state(
        TransactionFSM.description
    )

    await message.answer(
        "📝 Введите описание\n"
        "(или напишите -)"
    )


# ==========================
# ОПИСАНИЕ
# ==========================

@dp.message(TransactionFSM.description)
async def get_description(
    message: types.Message,
    state: FSMContext
):
    data = await state.get_data()

    description = (
        ""
        if message.text == "-"
        else message.text
    )

    add_transaction(
        user_id=message.from_user.id,
        amount=data["amount"],
        tx_type=data["type"],
        category=data["category"],
        description=description
    )

    await state.clear()

    emoji = (
        "💰"
        if data["type"] == "income"
        else "💸"
    )

    await message.answer(
        f"{emoji} Транзакция сохранена!",
        reply_markup=main_menu
    )


# ==========================
# БЫСТРОЕ ДОБАВЛЕНИЕ
# ==========================

@dp.message()
async def handle_transaction(message: types.Message):
    if not message.text:
        return

    parsed = parse_transaction(message.text)

    if not parsed:
        return

    add_transaction(
        user_id=message.from_user.id,
        amount=parsed["amount"],
        tx_type=parsed["type"],
        category=parsed["category"],
        description=parsed["description"]
    )

    emoji = (
        "💰"
        if parsed["type"] == "income"
        else "💸"
    )

    await message.answer(
        f"{emoji} Записано!\n"
        f"Категория: {parsed['category']}\n"
        f"Сумма: {parsed['amount']} ₽"
    )


# ==========================
# MAIN
# ==========================

async def main():
    init_db()

    print("✅ Бот запущен")

    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
