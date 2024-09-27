from aiogram.types import InlineKeyboardButton
from .database import sessionmaker
from .category_class import Category
from .services_class import Service
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
import sqlalchemy


async def get_categories()->list:
    async with sessionmaker() as session:
        session: AsyncSession
        request = sqlalchemy.select(Category)
        result = list(await session.scalars(request))
        return result


async def get_services_by_category(category)->list:
    async with sessionmaker() as session:
        session: AsyncSession
        request = sqlalchemy.select(Service).filter(Service.category == category)
        result = list(await session.scalars(request))
        return result


async def get_categories_keyboard(admin=False):
    categories = await get_categories()
    buttons = []
    for i in categories:
        buttons.append([InlineKeyboardButton(text=i.name, callback_data="category_"+str(i.id))])
    if admin:
        buttons.append([InlineKeyboardButton(text='Назад в меню↩️', callback_data='backtoadminservicemenu')])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def get_services_keyboard(category, admin=False):
    services = await get_services_by_category(category)
    buttons = []
    for i in services:
        buttons.append([InlineKeyboardButton(text=i.name, callback_data="service_"+str(i.id))])
    if admin:
        buttons.append([InlineKeyboardButton(text='Назад в меню↩️', callback_data='deleteservice')])
    else:
        buttons.append([InlineKeyboardButton(text='Назад в меню↩️', callback_data='choosecategory')])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

