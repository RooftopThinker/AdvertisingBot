from aiogram import Router, types, F
from aiogram.filters.state import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from aiogram.fsm.context import FSMContext
from data import get_categories_keyboard, get_services_keyboard, Service
from typing import Union
router = Router()


@router.callback_query(F.data == 'choosecategory', StateFilter(None))
@router.message(F.text == 'Каталог услуг', StateFilter(None))
async def choose_category(event: Union[types.Message,types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.Message):
        message = event
    else:
        message = event.message
        await event.message.delete()
    await message.answer('Выберите категорию', reply_markup=await get_categories_keyboard())
    await state.clear()

@router.callback_query(F.data.startswith('category_'), StateFilter(None))
async def choose_service(callback: types.CallbackQuery, state:FSMContext):
    data = int(callback.data.split('_')[1])
    await callback.message.delete()
    await callback.message.answer(text='Выберите услугу', reply_markup=await get_services_keyboard(data))
    await state.update_data(category=data)


@router.callback_query(F.data.startswith('service_'), StateFilter(None))
async def show_service(callback: types.CallbackQuery, session: AsyncSession):
    data = int(callback.data.split('_')[1])
    request = sqlalchemy.select(Service).filter(Service.id == data).limit(1)
    service = list(await session.scalars(request))[0]
    await callback.message.delete()
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Назад↩️", callback_data='back_to_choose_service')]])
    await callback.bot.copy_message(chat_id=callback.from_user.id, from_chat_id=service.chat_id,
                                    message_id=service.message_id, reply_markup=keyboard)


@router.callback_query(F.data == 'back_to_choose_service', StateFilter(None))
async def back_to_choose_service(callback: types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    callback = types.CallbackQuery(message=callback.message, data= f'category_{data['category']}',
                                   chat_instance=callback.chat_instance, from_user=callback.from_user, id=callback.id)
    await choose_service(callback, state)