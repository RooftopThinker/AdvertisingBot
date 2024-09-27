from aiogram import types, Bot
from aiogram.filters import Filter
from data import Admin
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy


class IsOwner(Filter):
    async def __call__(self, message: types.Message, session: AsyncSession, bot: Bot):
        request = sqlalchemy.select(Admin).filter(Admin.tg_id == message.from_user.id, Admin.is_owner == True).limit(1)
        results = list(await session.scalars(request))
        if not results:
            return False
        else:
            return True