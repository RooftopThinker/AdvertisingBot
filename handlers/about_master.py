from aiogram import Router, types, F
from aiogram.filters.state import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from aiogram.fsm.context import FSMContext
from data import AboutMaster, Document
import asyncio
from keyboards.menus import get_about_master_menu_keyboard
router = Router()
keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[types.InlineKeyboardButton(text="Назад↩️", callback_data='back_to_about_master')]])

@router.message(F.text == 'О мастере', StateFilter(None))
async def choose_category(message: types.Message, state: FSMContext):
    await message.answer('Выберите, что хотите узнать', reply_markup=get_about_master_menu_keyboard())
    await state.clear()


@router.callback_query(F.data.startswith('about_'), StateFilter(None))
async def about_master(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split('_')[1]
    request = sqlalchemy.select(AboutMaster).filter(AboutMaster.name == data)
    try:
        result: AboutMaster = list(await session.scalars(request))[0]
    except IndexError:
        await callback.message.answer('Этот раздел не был настроен')
        return
    await callback.message.delete()

    await callback.bot.copy_message(message_id=result.message_id, from_chat_id=result.chat_id,
                                    chat_id=callback.from_user.id, reply_markup=keyboard)


@router.callback_query(F.data == 'back_to_about_master')
async def back_to_about_master(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Выберите, что хотите узнать', reply_markup=get_about_master_menu_keyboard())


@router.callback_query(F.data == 'alldiplomas')
async def show_diplomas(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(Document)
    documents = list(await session.scalars(request))
    await callback.message.delete()
    for i in documents:
        await callback.bot.copy_message(chat_id=callback.from_user.id, from_chat_id=i.chat_id, message_id=i.message_id)
        await asyncio.sleep(0.06)
    await callback.message.answer('Перед Вами все дипломы и сертификаты, полученные Мастером', reply_markup=keyboard)
