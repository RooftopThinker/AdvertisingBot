from aiogram import types
from data import Admin

def get_start_keyboard():
    buttons = [[types.KeyboardButton(text="Каталог услуг")],
               [types.KeyboardButton(text="О мастере")],
               [types.KeyboardButton(text="Запись на сеанс")]]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    return keyboard


def get_admin_menu_keyboard():
    buttons = [[types.InlineKeyboardButton(text='Услуги', callback_data='manageservices')],
               [types.InlineKeyboardButton(text='О мастере', callback_data='manageabout')],
               # [types.InlineKeyboardButton(text='Офис', callback_data='manageoffice')],
               [types.InlineKeyboardButton(text='Администраторы', callback_data='manageadmins')]
               ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admin_services_menu_keyboard():
    buttons = [[types.InlineKeyboardButton(text="Добавить услугу", callback_data='addservice')],
               [types.InlineKeyboardButton(text="Удалить услугу", callback_data='deleteservice')],
               [types.InlineKeyboardButton(text="Удалить категорию", callback_data='deletecategory')],
               [types.InlineKeyboardButton(text="Изменить название категории", callback_data='changecategoryname')],
               [types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='backtoadminmenu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_about_master_menu_keyboard():
    buttons = [[types.InlineKeyboardButton(text="Сообщение при начале диалога", callback_data='manage_greetings')],
               [types.InlineKeyboardButton(text="Ссылка для записи на сеанс", callback_data='manage_link')],
               [types.InlineKeyboardButton(text="Опыт работы & Навыки", callback_data='manage_xp')],
               [types.InlineKeyboardButton(text="Образование, Дипломы & Сертификаты", callback_data='manage_diplomas')],
               [types.InlineKeyboardButton(text="Как добраться", callback_data='manage_location')],
               [types.InlineKeyboardButton(text="Интерьер & Удобства", callback_data='manage_interior')],
               [types.InlineKeyboardButton(text="Отзывы", callback_data='manage_reviews')],
               [types.InlineKeyboardButton(text="Система скидок", callback_data='manage_discounts')],
               [types.InlineKeyboardButton(text="Подарочные сертификаты", callback_data='manage_gifts')],
               [types.InlineKeyboardButton(text="Назад в меню↩️", callback_data='backtoadminmenu')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_admin_preferences_keyboard(admin: Admin, requestor: Admin):
    can_promote = '✅' if admin.can_promote_admin else '❌'
    buttons = [[types.InlineKeyboardButton(text='Может добавлять администраторов:'+can_promote,
                                           callback_data='promote_'+str(admin.id))]]
    if (admin.promoted_by == requestor.id and not admin.is_owner) or requestor.is_owner:
        buttons.append([types.InlineKeyboardButton(text='Удалить из администраторов',
                                                   callback_data='removeadmin_'+str(admin.id))])
    if requestor.is_owner:
        buttons.append([types.InlineKeyboardButton(text='Передать владение ботом',
                                                   callback_data='transefownership_' + str(admin.id))])
    buttons.append([types.InlineKeyboardButton(text='Назад в меню↩️',
                                                   callback_data='manageadmins')])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_about_master_menu_keyboard():
    buttons = [[types.InlineKeyboardButton(text="Как добраться", callback_data='about_location')],
               [types.InlineKeyboardButton(text="Опыт работы & Навыки", callback_data='about_xp')],
               [types.InlineKeyboardButton(text="Образование, Дипломы & Сертификаты", callback_data='alldiplomas')],
               [types.InlineKeyboardButton(text="Интерьер & Удобства", callback_data='about_interior')],
               [types.InlineKeyboardButton(text="Отзывы", callback_data='about_reviews')],
               [types.InlineKeyboardButton(text="Система скидок", callback_data='about_discounts')],
               [types.InlineKeyboardButton(text="Подарочные сертификаты", callback_data='about_gifts')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard