"""
Import all submodules for dependency graph generation with pydeps.
This file imports all modules in the cosmic-django project to help pydeps
generate a complete dependency graph.

Uncomment the imports below before running pydeps.
"""

# # Core Django settings and configuration
# from cosmic.settings import base, test
# from cosmic import urls
# from cosmic import wsgi
# from cosmic import asgi

# # Allocation app modules
# from allocation import models as allocation_models
# from allocation import views as allocation_views
# from allocation import admin as allocation_admin
# from allocation import apps as allocation_apps
# from allocation import managers as allocation_managers
# from allocation import signals as allocation_signals

# # Core app modules
# from core import models as core_models
# from core import views as core_views
# from core import admin as core_admin
# from core import apps as core_apps

# # Core logic modules
# from core.logic import logic

# # Core service modules
# from core.service import service

# # Core test modules (importing the test modules themselves)
# from core.tests import test_api
# from core.tests import test_batches
# from core.tests import test_email
# from core.tests import test_external_events
# from core.tests import test_handlers
# from core.tests import test_product
# from core.tests import test_repository
# from core.tests import test_uow
# from core.tests import test_views
# from core.tests import conftest

# # List all imported modules for reference
# __all__ = [
#     # Settings
#     'base', 'test',
#     # Django config
#     # Allocation app
#     'allocation_models', 'allocation_views', 'allocation_admin', 
#     'allocation_apps', 'allocation_managers', 'allocation_signals',
#     # Core app
#     'core_models', 'core_views', 'core_admin', 'core_apps',
#     # Logic and service layers
#     'logic', 'service',
# ]
