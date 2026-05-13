from aiogram.fsm.state import State, StatesGroup


class TransactionFSM(StatesGroup):
    type = State()          # income / expense
    amount = State()
    category = State()
    description = State()