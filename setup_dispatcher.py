from handlers import (menu_router, start_router, service_management_router,
                      about_master_management_router, admins_management_router,
                      become_admin_router, services_router, sign_up_router, about_master_router)
from aiogram import Dispatcher
from middlewares.db import DbSessionMiddleware
from data.database import sessionmaker
async def setup_dispatcher(dispatcher: Dispatcher):
    dispatcher.include_routers(start_router,
                               menu_router,
                               service_management_router,
                               about_master_management_router,
                               admins_management_router,
                               become_admin_router,
                               services_router, sign_up_router, about_master_router)
    dispatcher.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
