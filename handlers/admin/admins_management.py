import sqlalchemy
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from filters import IsAdmin, IsOwner
from data import Admin
from handlers.fsm import ManageAdmins, NewAdmin
from keyboards.menus import get_admin_preferences_keyboard
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import asyncio
router = Router()
router.callback_query.filter(IsAdmin())
router.message.filter(IsAdmin())


@router.callback_query(F.data == 'manageadmins')
async def admins_list(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    request = sqlalchemy.select(Admin).order_by(sqlalchemy.desc(Admin.is_owner), sqlalchemy.desc(Admin.can_promote_admin))
    result = list(await session.scalars(request))
    request = sqlalchemy.select(Admin).filter(Admin.tg_id == callback.from_user.id).limit(1)
    requestor: Admin = list(await session.scalars(request))[0]
    await state.update_data(requestor=requestor)
    buttons = []
    for i in result:
        if i.is_owner:
            buttons.append([types.InlineKeyboardButton(text=i.username + '👑', callback_data='admin_'+str(i.id))])
        elif i.can_promote_admin:
            buttons.append([types.InlineKeyboardButton(text=i.username + '🎩', callback_data='admin_' + str(i.id))])
        else:
            buttons.append([types.InlineKeyboardButton(text=i.username, callback_data='admin_' + str(i.id))])
    if requestor.can_promote_admin:
        buttons.append([types.InlineKeyboardButton(text='Добавить администратора ➕', callback_data='newadmin')])
    buttons.append([types.InlineKeyboardButton(text='Назад в меню↩️', callback_data='backtoadminmenu')])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("Список администраторов:", reply_markup=keyboard)


@router.callback_query(F.data.startswith('admin_'))
async def manage_admin(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.delete()
    data = int(callback.data.split('_')[1])
    request = sqlalchemy.select(Admin).filter(Admin.id == data)
    admin = list(await session.scalars(request))[0]
    await state.update_data(admin=admin)
    data = await state.get_data()
    await state.set_state(ManageAdmins.choose_action)
    await callback.message.answer(f'{admin.username}',
                                  reply_markup=get_admin_preferences_keyboard(admin=admin, requestor=data['requestor']))


@router.callback_query(F.data.startswith('promote_'), ManageAdmins.choose_action)
async def switch_promotion_ability(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    if not data['requestor'].is_owner:
        await callback.answer('Недостаточно прав')
        return
    if data['requestor'].id == data['admin'].id:
        await callback.answer("У себя нельзя забрать права")
        return
    request = sqlalchemy.update(Admin).filter(Admin.id == data['admin'].id).values(
        can_promote_admin=not data['admin'].can_promote_admin)
    await session.execute(request)
    await session.commit()
    data['admin'].can_promote_admin = not data['admin'].can_promote_admin
    await callback.message.edit_reply_markup(reply_markup=get_admin_preferences_keyboard(
        admin=data['admin'], requestor=data['requestor']))


@router.callback_query(F.data.startswith('removeadmin_'), ManageAdmins.choose_action)
async def remove_admin(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    id = int(callback.data.split('_')[1])
    data = await state.get_data()
    if data['requestor'].id == data['admin'].id:
        await callback.answer('Удалить себя нельзя')
        return
    if (not data['requestor'].is_owner and data['admin'].promoted_by != data['requestor'].id) or data['admin'].is_owner:
        await callback.answer('Недостаточно прав')
        return
    request = sqlalchemy.delete(Admin).filter(Admin.id == id)
    await session.execute(request)
    await session.commit()
    await callback.answer(f'{data['admin'].username} удалён из списка администраторов')
    await admins_list(callback, session, state)


@router.callback_query(F.data.startswith('transefownership_'), IsOwner())
async def transfer_ownership_approval(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['requestor'].id == data['admin'].id:
        await callback.answer('Вы и так тут босс')
        return
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="✅", callback_data='approvetransferownership')],
                         [types.InlineKeyboardButton(text="Назад", callback_data='backtoadmininfo')]])
    await callback.message.edit_text(f"Вы уверены, что хотите передать права на бота пользователю {data['admin'].username}?"
                                  f" Это действие необратимо.", reply_markup=keyboard)


@router.callback_query(F.data == 'approvetransferownership', IsOwner())
async def transfer_ownership(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(f'{data['admin'].username} теперь владеет этим ботом', reply_markup=None)
    request = sqlalchemy.update(Admin).filter(Admin.id == data['admin'].id).values(is_owner=True, can_promote_admin=True)
    await session.execute(request)
    request = sqlalchemy.update(Admin).filter(Admin.id == data['requestor'].id).values(is_owner=False)
    await session.execute(request)
    await session.commit()
    try:
        await callback.bot.send_message(chat_id=data['admin'].tg_id, text=f'{data['requestor'].username} передал Вам владение ботом')
    except TelegramForbiddenError:
        pass
    await admins_list(callback, session, state)


@router.callback_query(F.data == 'backtoadmininfo')
async def back_to_admin_info(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    callback = types.CallbackQuery(message=callback.message, data= f'admin_{data['admin'].id}',
                                   chat_instance=callback.chat_instance, from_user=callback.from_user, id=callback.id)
    await manage_admin(callback, session, state)


@router.callback_query(F.data == 'newadmin')
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data['requestor'].can_promote_admin:
        await callback.answer('Недостаточно прав')
        return
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='manageadmins')]])
    await callback.message.edit_text(text='Перешлите сообщение от пользователя, которого хотите добавить в администраторы.',
                                     reply_markup=keyboard)
    await state.set_state(NewAdmin.add_admin)


@router.message(NewAdmin.add_admin, F.forward_from.id)
async def admin_added(message: types.Message, session: AsyncSession, state: FSMContext):
    request = sqlalchemy.select(Admin).filter(Admin.tg_id == message.from_user.id).limit(1)
    requestor = list(await session.scalars(request))[0]

    admin = Admin(username='@'+message.forward_from.username, tg_id=message.forward_from.id, promoted_by=requestor.id)
    session.add(admin)
    await state.clear()
    try:
        await session.commit()
    except sqlalchemy.exc.IntegrityError:
        await session.rollback()
        await message.answer('Этот пользователь уже находится в списке администраторов')
        return
    await message.answer(f"Пользователь {message.forward_from.username} добавлен в список администраторов")
    try:
        await message.bot.send_message(chat_id=message.forward_from.id, text=f'{message.from_user.username} '
                                                                             f'добавил вас в администраторы этого бота')
    except (TelegramBadRequest, TelegramForbiddenError):
        return
    await message.bot.set_my_commands(commands=[types.BotCommand(command='start', description='перезапустить бота если пропали кнопки'),
                                                types.BotCommand(command='menu', description='открыть меню')],
                                      scope=types.bot_command_scope_chat.BotCommandScopeChat(chat_id=message.forward_from.id))

@router.message(NewAdmin.add_admin, ~F.forward_from.id)
async def admin_added(message: types.Message):
    await message.answer('Сообщение не было распознано как пересланное. Возможно, у пользователя стоят настройки приватности,'
                         'запрещающие пересылку. Попробуйте ещё раз')
