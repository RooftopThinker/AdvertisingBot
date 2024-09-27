from aiogram import Router, types, F
from aiogram.filters.state import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from aiogram.fsm.context import FSMContext
from data import AboutMaster
router = Router()


@router.message(F.text == 'Запись на сеанс', StateFilter(None))
async def sign_up(message: types.Message, state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(AboutMaster).filter(AboutMaster.name == 'link')
    try:
        result: AboutMaster = list(await session.scalars(request))[0]
    except IndexError:
        await message.answer('Этот раздел не был настроен')
        return
    await message.bot.copy_message(chat_id=message.chat.id, from_chat_id=result.chat_id, message_id=result.message_id)
    await state.clear()
