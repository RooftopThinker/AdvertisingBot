from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from data import AboutMaster
from keyboards.menus import get_start_keyboard
router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    request = sqlalchemy.select(AboutMaster).filter(AboutMaster.name == 'greetings').limit(1)
    try:
        result: AboutMaster = list(await session.scalars(request))[0]
    except IndexError:
        await message.answer('Стартовое сообщение не настроено')
        return
    await message.bot.copy_message(message_id=result.message_id, from_chat_id=result.chat_id, chat_id=message.chat.id,
                                   reply_markup=get_start_keyboard())