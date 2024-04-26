#API endpoints for products
from django.http import JsonResponse
from django.contrib.auth import authenticate

from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from Accounts.models import CustomUser
# from .models import Store
# from .serializers import StoreSerializer

import json