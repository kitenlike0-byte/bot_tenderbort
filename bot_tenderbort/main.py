import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from db import init_db
from db import add_transaction
from utils.parser import parse_transaction
from db import get_balance
from db import get_stats, get_last_transactions
from keyboards.main_menu import main_menu
from db import get_category_stats
from utils.categories import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES
)
from db import get_category_stats

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# /start команда
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в финансового бота!\n\n"
        "Записывай доходы и расходы прямо сообщением.\n"
        "Пример:\n"
        "-500 еда\n"
        "+2000 зарплата",
        reply_markup=main_menu
    )

@dp.message(Command("balance"))
async def balance(message: types.Message):
    user_id = message.from_user.id

    balance = get_balance(user_id)

    await message.answer(
        f"💳 Текущий баланс: {balance} ₽"
    )



@dp.message(Command("stats"))
async def stats(message: types.Message):
    user_id = message.from_user.id

    stats_data = get_stats(user_id)
    transactions = get_last_transactions(user_id)

    text = (
        "💳 <b>Финансовый отчёт</b>\n\n"

        f"💰 Баланс: <b>{stats_data['balance']} ₽</b>\n\n"

        f"📈 Доходы: +{stats_data['income']} ₽\n"
        f"📉 Расходы: -{stats_data['expense']} ₽\n\n"

        "🕒 <b>Последние операции:</b>\n"
    )

    if not transactions:
        text += "\nНет операций."
    else:
        for amount, tx_type, category in transactions:

            emoji = "💰" if tx_type == "income" else "💸"

            text += (
                f"{emoji} {amount} ₽ | {category}\n"
            )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@dp.message()
async def handle_message(message: types.Message):
    parsed = parse_transaction(message.text)

    if not parsed:
        await message.answer(
            "❌ Не понял формат.\n"
            "Пример:\n"
            "-500 еда\n"
            "+2000 зарплата"
        )
        return

    user_id = message.from_user.id

    add_transaction(
        user_id=user_id,
        amount=parsed["amount"],
        tx_type=parsed["type"],
        category=parsed["category"],
        description=parsed["description"]
    )

    if parsed["type"] == "expense":
        emoji = "💸"
    else:
        emoji = "💰"

    await message.answer(
        f"{emoji} Записано!\n"
        f"Категория: {parsed['category']}\n"
        f"Сумма: {parsed['amount']}"
    )


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await dp.start_polling(bot)

     @dp.message(lambda message: message.text == "💳 Баланс")
async def balance_button(message: types.Message):

    user_id = message.from_user.id
    balance = get_balance(user_id)

    await message.answer(
        f"💳 Твой баланс: {balance} ₽"
    )


from aiogram.fsm.state import State, StatesGroup


class TransactionFSM(StatesGroup):
    type = State()          # income / expense
    amount = State()
    category = State()
    description = State()


    @dp.message(lambda message: message.text == "📊 Статистика")
async def stats_button(message: types.Message):

    user_id = message.from_user.id

    stats_data = get_stats(user_id)
    transactions = get_last_transactions(user_id)
    category_stats = get_category_stats(user_id)
text += "\n📂 <b>Категории расходов:</b>\n"

for category, amount in category_stats:
    text += f"• {category}: {amount} ₽\n"
    text = (
        "📊 <b>Статистика</b>\n\n"

        f"💰 Баланс: {stats_data['balance']} ₽\n"
        f"📈 Доходы: +{stats_data['income']} ₽\n"
        f"📉 Расходы: -{stats_data['expense']} ₽\n\n"

        "🕒 Последние операции:\n"
    )

    for amount, tx_type, category in transactions:

        emoji = "💰" if tx_type == "income" else "💸"

        text += f"{emoji} {amount} ₽ | {category}\n"

    await message.answer(
        text,
        parse_mode="HTML"
    )

    @dp.message(lambda message: message.text == "⚠️ Жалоба")
async def complaint(message: types.Message):

    await message.answer(
        "Опишите проблему следующим сообщением."
    )

    await bot.send_message(
    ADMIN_ID,
    f"⚠️ Жалоба:\n\n{message.text}"
) 

    @dp.message(lambda message: message.text == "➕ Доход")
async def income_start(message: types.Message, state: FSMContext):

    await state.set_state(TransactionFSM.amount)
    await state.update_data(type="income")

    await message.answer("💰 Введите сумму дохода:")

    @dp.message(lambda message: message.text == "➖ Расход")
async def expense_start(message: types.Message, state: FSMContext):

    await state.set_state(TransactionFSM.amount)
    await state.update_data(type="expense")

    await message.answer("💸 Введите сумму расхода:")

    @dp.message(TransactionFSM.amount)
async def get_amount(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ Введите число")
        return

    await state.update_data(amount=int(message.text))
    data = await state.get_data()

    categories = INCOME_CATEGORIES if data["type"] == "income" else EXPENSE_CATEGORIES

    text = "📂 Выберите категорию:\n\n" + "\n".join(categories)

    await state.set_state(TransactionFSM.category)
    await message.answer(text)

    @dp.message(TransactionFSM.category)
async def get_category(message: types.Message, state: FSMContext):

    await state.update_data(category=message.text)

    await state.set_state(TransactionFSM.description)
    await message.answer("📝 Введите описание (или напишите '-'):")

    @dp.message(TransactionFSM.description)
async def get_description(message: types.Message, state: FSMContext):

    data = await state.get_data()

    description = message.text if message.text != "-" else ""

    add_transaction(
        user_id=message.from_user.id,
        amount=data["amount"],
        tx_type=data["type"],
        category=data["category"],
        description=description
    )

    await state.clear()

    await message.answer(
        "✅ Транзакция сохранена!",
        reply_markup=main_menu
    )
