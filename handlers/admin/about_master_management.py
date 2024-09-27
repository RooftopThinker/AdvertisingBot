import sqlalchemy
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from filters import IsAdmin
from data import AboutMaster, Document
from handlers.fsm import ManageSection, ManageDocuments
from keyboards.menus import get_admin_about_master_menu_keyboard, get_start_keyboard
import asyncio
router = Router()
router.callback_query.filter(IsAdmin())
router.message.filter(IsAdmin())


@router.callback_query(F.data == 'manageabout')
async def manage_services(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Выберите опцию из списка", reply_markup=get_admin_about_master_menu_keyboard())


@router.callback_query(F.data.startswith('manage_'), F.data!='manage_diplomas')
async def manage(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = callback.data.split('_')[1]
    await state.update_data(section=data)
    await callback.message.delete()
    buttons = [[types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='backtoadminaboutmastermenu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    request = sqlalchemy.select(AboutMaster).filter(AboutMaster.name == data).limit(1)
    result = list(await session.scalars(request))
    if result:
        await callback.message.answer('Сейчас при нажатии на эту кнопку бот показывает сообщение:')
        await callback.bot.copy_message(chat_id=callback.from_user.id, message_id=result[0].message_id,
                                        from_chat_id=result[0].chat_id)
    await callback.message.answer("Укажите сообщение, которое бот отправит при нажатии пользователем на эту кнопку",
                                  reply_markup=keyboard)
    await state.set_state(ManageSection.message)


@router.message(ManageSection.message)
async def override(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    info = AboutMaster(name=data['section'], message_id=message.message_id, chat_id=message.chat.id)
    await session.merge(info)
    await session.commit()
    await message.answer("Теперь при нажатии на эту кнопку бот ответит этим сообщением:")
    await message.bot.copy_message(from_chat_id=message.chat.id, chat_id=message.chat.id, message_id=message.message_id)
    await state.clear()


@router.callback_query(F.data == 'manage_diplomas')
async def manage_diplomas(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    buttons = [[types.InlineKeyboardButton(text="Добавить документы", callback_data='adddocs')],
               [types.InlineKeyboardButton(text="Удалить документ", callback_data='deletedocs')],
               [types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='backtoadminaboutmastermenu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("Выберите действие", reply_markup=keyboard)


@router.callback_query(F.data == 'adddocs')
async def add_docs(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    buttons = [[types.KeyboardButton(text='Завершить')]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    await callback.message.answer("Отправьте боту все фото документов с описанием или без, которые хотите добавить в раздел"
                                  " 'Образование, Дипломы & Сертификаты'. Когда закончите, нажмите на клавиатурную кнопку внизу"
                                  " или напишите 'Завешить'", reply_markup=keyboard)
    await state.set_state(ManageDocuments.add_documents)


@router.message(ManageDocuments.add_documents, F.photo)
async def retrieve_docs(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.message_id)
    await state.update_data(photos=photos)


@router.message(ManageDocuments.add_documents, F.text == 'Завершить')
async def finish(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        for i in data['photos']:
            doc = Document(chat_id=message.chat.id, message_id=i)
            session.add(doc)
        await session.commit()
        await message.answer(f'Добавлено {len(data['photos'])} документов', reply_markup=get_start_keyboard())
    except KeyError:
        await message.answer('Ни одного документа не было добавлено', reply_markup=get_start_keyboard())
    await state.clear()


@router.callback_query(F.data == 'deletedocs')
async def delete_docs(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(Document)
    buttons = [[types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='backtoadminaboutmastermenu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    result = list(await session.scalars(request))
    buttons = [[types.KeyboardButton(text='Завершить')]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    await callback.message.answer("Нажмите кнопки под документами, которые хотите удалить. После того, как все"
                                  "нужные документы выбраны, нажмите на клавиатурную кнопку или напишите 'Завершить'",
                                  reply_markup=keyboard)
    await asyncio.sleep(2)
    for i in result:
        buttons = [[types.InlineKeyboardButton(text='🗑️', callback_data=f'deletedocument_{i.id}')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.bot.copy_message(message_id=i.message_id, from_chat_id=i.chat_id, chat_id=callback.message.chat.id,
                                        reply_markup=keyboard)
        await asyncio.sleep(0.05)
    await state.set_state(ManageDocuments.delete_documents)


@router.callback_query(F.data.startswith('deletedocument_'), ManageDocuments.delete_documents)
async def add_docs_to_list(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    docs = data.get('docs', [])
    id = int(callback.data.split('_')[1])
    if id in docs:
        docs.remove(id)
        buttons = [[types.InlineKeyboardButton(text='🗑️', callback_data=callback.data)]]
    else:
        docs.append(id)
        buttons = [[types.InlineKeyboardButton(text='🗑️✅', callback_data=callback.data)]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.update_data(docs=docs)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.message(F.text == "Завершить", ManageDocuments.delete_documents)
async def finish_deleting_docs(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    try:
        for i in data['docs']:
            request = sqlalchemy.delete(Document).filter(Document.id == i)
            await session.execute(request)
        await session.commit()
        await message.answer(f"Выбранные документы ({len(data['docs'])}) успешно удалены", reply_markup=get_start_keyboard())
    except KeyError:
        await message.answer("Ни один документ не был удалён", reply_markup=get_start_keyboard())
    await state.clear()

