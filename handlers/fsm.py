from aiogram.fsm.state import State, StatesGroup


class AddService(StatesGroup):
    category = State()
    name = State()
    description = State()
    image = State()


class DeleteService(StatesGroup):
    category = State()
    name = State()
    approval = State()


class ChangeCategoryName(StatesGroup):
    category = State()
    name = State()


class DeleteCategory(StatesGroup):
    category = State()
    approval = State()


class ManageSection(StatesGroup):
    message = State()


class ManageDocuments(StatesGroup):
    add_documents = State()
    delete_documents = State()


class ManageAdmins(StatesGroup):
    choose_action = State()


class NewAdmin(StatesGroup):
    add_admin = State()
