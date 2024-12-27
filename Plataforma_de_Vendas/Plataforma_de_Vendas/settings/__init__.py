import os

ENVIRONMENT = os.getenv('PLATAFORMA_DJANGO_ENV', 'local')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .local import *