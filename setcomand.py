import asyncio

import config
from aiogram import Bot, types
bot = Bot(token=config.BOT_TOKEN)
asyncio.run(bot.set_my_commands(commands=[types.BotCommand(command='start', description='перезапустить бота если пропали кнопки'),
                                                types.BotCommand(command='menu', description='открыть меню')],
                                      scope=types.bot_command_scope_chat.BotCommandScopeChat(chat_id=125729731)))