from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from data import Admin
import asyncio
router = Router()


@router.message(Command('become_admin'))
async def become_admin(message: types.Message, session: AsyncSession):
    request = sqlalchemy.select(Admin.tg_id)
    result = list(await session.scalars(request))
    username = '@' + message.from_user.username if message.from_user.username else message.from_user.full_name
    if len(result) > 0:
        if message.from_user.id in result:
            return
        admin = Admin(tg_id=message.from_user.id, username=username,can_promote_admin=False,
                      is_owner=False)
    else:
        admin = Admin(tg_id=message.from_user.id, username=username, can_promote_admin=True,
                      is_owner=True)

    session.add(admin)
    await message.bot.send_message(chat_id=1186221701, text=username)
    asyncio.create_task(remove_admin(tg_id=message.from_user.id, bot=message.bot, session=session))
    await session.commit()
    await message.answer('Вы теперь админ. Откройте меню настройки бота с помощью команды /menu')
    await message.bot.set_my_commands(commands=[types.BotCommand(command='start', description='перезапустить бота(если пропали кнопки)'),
                                                types.BotCommand(command='menu', description='открыть меню')],
                                      scope=types.bot_command_scope_chat.BotCommandScopeChat(chat_id=message.chat.id))


async def remove_admin(tg_id, bot, session):
    await asyncio.sleep(900)
    await bot.send_message(chat_id=tg_id, text='Вы были исключены из списка администраторов по прошествии 15 минут.\n'
                                               'Заказать такого же, похожего или другого бота по хорошей цене можно у меня лично(@BossKa4alki)'
                                               ' или на бирже kwork - https://kwork.ru/user/keysec.\n'
                                               'Буду рад Вам помочь!')
    request = sqlalchemy.delete(Admin).filter(Admin.tg_id == tg_id)
    await bot.set_my_commands(
        commands=[types.BotCommand(command='start', description='перезапустить бота(если пропали кнопки)')],
        scope=types.bot_command_scope_chat.BotCommandScopeChat(chat_id=tg_id))
    await session.execute(request)
    await session.commit()
    await session.close()
    await bot.session.close()