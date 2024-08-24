"""
WSGI config for Plataforma_de_Vendas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

path = '/home/'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plataforma_de_Vendas.settings')

application = get_wsgi_application()

