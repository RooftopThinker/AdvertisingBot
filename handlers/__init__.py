from .start import router as start_router
from .admin.menu import router as menu_router
from .admin.service_management import router as service_management_router
from .admin.about_master_management import router as about_master_management_router
from .admin.admins_management import router as admins_management_router
from .admin.become_admin import router as become_admin_router
from .services import router as services_router
from .sign_up import router as sign_up_router
from .about_master import router as about_master_router

__all__ = ['start_router', 'menu_router', 'service_management_router', 'about_master_management_router',
           'admins_management_router', 'become_admin_router', 'services_router', 'sign_up_router',
           'about_master_router']
