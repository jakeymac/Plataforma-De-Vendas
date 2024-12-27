from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'plataforma-de-vendas',
        'USER': 'jmjohnson1578',
        'PASSWORD': 'password',
        'HOST': 'plataforma-de-vendas.czgoyism6zh2.us-east-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}