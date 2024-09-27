from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters import IsAdmin
from keyboards.menus import (get_admin_menu_keyboard, get_admin_services_menu_keyboard,
                             get_admin_about_master_menu_keyboard)
from typing import Union
router = Router()
router.message.filter(IsAdmin())


@router.callback_query(F.data == 'backtoadminmenu')
@router.message(Command('menu'))
async def menu(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        await event.message.delete()
        message = event.message
    else:
        message = event
    await state.clear()
    await message.answer("Выберите, что хотите настроить", reply_markup=get_admin_menu_keyboard())


@router.callback_query(F.data == 'backtoadminservicemenu')
async def service_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer("Выберите, что хотите настроить", reply_markup=get_admin_services_menu_keyboard())


@router.callback_query(F.data == 'backtoadminaboutmastermenu')
async def about_master_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer("Выберите, что хотите настроить", reply_markup=get_admin_about_master_menu_keyboard())


