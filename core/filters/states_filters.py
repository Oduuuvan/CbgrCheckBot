from aiogram.fsm.state import StatesGroup, State


class StateReasonNotWork(StatesGroup):
    GET_REASON = State()


class StateFIO(StatesGroup):
    GET_FIO = State()
