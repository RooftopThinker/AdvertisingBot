import asyncio
import logging
# from asyncio import WindowsSelectorEventLoopPolicy

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from setup_dispatcher import setup_dispatcher
import config
from data.database import SqlAlchemyBase, engine
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
# asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
dp = Dispatcher()

# @dp.message()
# async def echo(message: types.Message):
#     await message.answer(str(message.forward_from.id))

async def create_metadata():
    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)


async def main():
    await setup_dispatcher(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(create_metadata())
    asyncio.run(main())
