import sqlalchemy
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

import data
from filters import IsAdmin
from data import get_categories_keyboard, Service, get_services_keyboard, Category
from handlers.fsm import AddService, DeleteService, ChangeCategoryName, DeleteCategory
from typing import Union
from keyboards.menus import get_admin_menu_keyboard, get_admin_services_menu_keyboard
router = Router()
router.callback_query.filter(IsAdmin())
router.message.filter(IsAdmin())


async def send_message_split(image, bot, chat_id, text: str, **kwargs):
    max_length = 1024 if image else 4096
    if len(text) <= max_length:
        return await bot.send_message(chat_id, text, **kwargs)

    parts = []
    while len(text) > 0:
        if len(text) > max_length:
            part = text[:max_length]
            first_lnbr = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                text = text[first_lnbr:]
            else:
                parts.append(part)
                text = text[max_length:]
            max_length = 4096
        else:
            parts.append(text)
            break

    msg = None
    for part in parts:
        msg = await bot.send_message(chat_id, part, **kwargs)
    return msg


@router.callback_query(F.data == 'manageservices')
async def manageservices(callback: types.CallbackQuery):
    await callback.message.delete()

    await callback.message.answer("Выберите опцию из списка", reply_markup=get_admin_services_menu_keyboard())


@router.callback_query(F.data == 'addservice')
async def add_service(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите категорию. Чтобы создать новую, напишите её название",
                                  reply_markup=await get_categories_keyboard(admin=True))
    await state.set_state(AddService.category)
    await callback.message.delete()


@router.message(F.text, AddService.category)
@router.callback_query(AddService.category)
async def choose_category(event: Union[types.CallbackQuery, types.Message], state: FSMContext, session: AsyncSession):
    if isinstance(event, types.CallbackQuery):
        await state.update_data(category=int(event.data.split('_')[1]))
        await event.message.delete()
        await event.message.answer("Напишите имя услуги")
    else:
        category = Category(name=event.text)
        session.add(category)
        await session.commit()
        await session.refresh(instance=category)
        await state.update_data(category=category.id)
        await event.answer("Напишите имя услуги")
    await state.set_state(AddService.name)


@router.message(AddService.name)
async def choose_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddService.description)
    await message.answer("Отправьте описание услуги - сообщение,"
                         " которое будет показываться при клике на кнопку с именем услуги.")


# @router.message(F.text, AddService.description)
# async def choose_description(message: types.Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state(AddService.image)
#     keyboard = types.InlineKeyboardMarkup(
#         inline_keyboard=[[types.InlineKeyboardButton(text='Без картинки', callback_data='noimage')]])
#     await message.answer("Если хотите, пришлите картинку, чтобы добавить её к описанию", reply_markup=keyboard)


@router.message(AddService.description)
async def finish_creating_service(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await message.answer(f'Готово! Услуга "{data['name']}" добавлена')
    service = Service(name=data['name'], category=data['category'], message_id=message.message_id, chat_id=message.chat.id)
    session.add(service)
    await session.commit()
    await state.clear()


# @router.callback_query(F.data == 'noimage')
# async def no_image(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     data = await state.get_data()
#     await callback.message.answer(f'Готово! Услуга "{data['name']}" добавлена в категорию "{data["category"]}"')
#     service = Service(name=data['name'], category=data['category'], description=data['description'])
#     session.add(service)
#     await session.commit()
#     await state.clear()


@router.callback_query(F.data == 'deleteservice')
async def delete_service(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите категорию",
                                  reply_markup=await get_categories_keyboard(admin=True))
    await state.set_state(DeleteService.category)
    await callback.message.delete()


@router.callback_query(DeleteService.category, F.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    category = int(callback.data.split("_")[1])
    await state.update_data(category=category)
    await callback.message.answer(text='Выберите услугу', reply_markup=await get_services_keyboard(category, True))
    await state.set_state(DeleteService.name)


@router.callback_query(DeleteService.name, F.data.startswith("service_"))
async def approval(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="✅", callback_data='delservice_approve')],
                         [types.InlineKeyboardButton(text="Назад", callback_data='delservice_back')]])
    await callback.message.answer("Вы уверены?", reply_markup=keyboard)
    await state.update_data(service=int(callback.data.split("_")[1]))
    await state.set_state(DeleteService.approval)


@router.callback_query(DeleteService.approval, F.data.in_({'delservice_approve', 'delservice_back'}))
async def choose_approval(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await callback.message.delete()
    if callback.data == 'delservice_approve':
        request = sqlalchemy.delete(Service).filter(Service.id == data['service'])
        await session.execute(request)
        await session.commit()
        await callback.message.answer('Успешно удалено', reply_markup=get_admin_menu_keyboard())
        await state.clear()
    else:
        await callback.message.answer(text='Выберите услугу', reply_markup=await get_services_keyboard(data['category'], True))
        await state.set_state(DeleteService.name)


@router.callback_query(F.data == 'backtoservicesadminlist')
# async def back_to_services_list(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     await callback.message.edit_text(text='Выберите категорию',
#                                   reply_markup=await get_categories_keyboard(True))

@router.callback_query(F.data == 'changecategoryname')
async def change_category_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="Выберите категорию", reply_markup=await get_categories_keyboard(admin=True))
    await state.set_state(ChangeCategoryName.category)


@router.callback_query(ChangeCategoryName.category, F.data.startswith("category_"))
async def category_chosen(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    category = int(callback.data.split("_")[1])

    request = sqlalchemy.select(Category).filter(Category.id == category).limit(1)
    result = list(await session.scalars(request))[0].name
    await state.update_data(category=category, name=result)
    await callback.message.answer("Введите новое название для категории " + result)
    await state.set_state(ChangeCategoryName.name)


@router.message(ChangeCategoryName.name, F.text)
async def changed_category_name(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    request = sqlalchemy.update(Category).filter(Category.id == data['category']).values(name=message.text)
    await session.execute(request)
    await session.commit()
    await state.clear()
    await message.answer(f"Название категории {data['name']} изменено на {message.text}")


@router.callback_query(F.data == 'deletecategory')
async def delete_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="Выберите категорию", reply_markup=await get_categories_keyboard(admin=True))
    await state.set_state(DeleteCategory.category)


@router.callback_query(DeleteCategory.category, F.data.startswith("category_"))
async def category_chosen(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    category = int(callback.data.split("_")[1])
    await state.update_data(category=category)
    request = sqlalchemy.select(Category).filter(Category.id == category).limit(1)
    result = list(await session.scalars(request))[0].name

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="✅", callback_data='delcategory_approve')],
                         [types.InlineKeyboardButton(text="Назад", callback_data='delcategory_back')]])
    await callback.message.answer("Подтверждаете удалении категории " + result + '?', reply_markup=keyboard)
    await state.set_state(DeleteCategory.approval)


@router.callback_query(DeleteCategory.approval, F.data.in_({'delcategory_approve', 'delcategory_back'}))
async def choose_approval(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await callback.message.delete()
    if callback.data == 'delcategory_approve':
        request = sqlalchemy.delete(Category).filter(Category.id == data['category'])
        await session.execute(request)
        request = sqlalchemy.delete(Service).filter(Service.category == data['category'])
        await session.execute(request)
        await session.commit()
        await callback.message.answer('Успешно удалено')
        await state.clear()
    else:
        await callback.message.answer(text='Выберите услугу', reply_markup=await get_services_keyboard(data['category'], True))
        await state.set_state(DeleteCategory.category)