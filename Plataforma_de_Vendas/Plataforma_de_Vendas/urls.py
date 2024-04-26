"""
URL configuration for Plataforma_de_Vendas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from Accounts import views as account_views, endpoints as account_endpoints
from Orders import views as order_views, endpoints as order_endpoints
from Products import views as product_views, endpoints as product_endpoints
from Stores import views as store_views, endpoints as store_endpoints


schema_view = get_schema_view(
    openapi.Info(
        title="NAME HERE API Documentation",
        default_version='v1',
        description="""This API provides seamless access to the NAME HERE system's 
        functionalites for managing products, inventory, orders,
        user accounts of both store owners and customers""",
        contact=openapi.Contact(email="jmjohnson1578@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', store_views.home, name='home'),
    path('swagger/',schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/swagger/',schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/stores/',store_endpoints.get_stores_endpoint),
    path('api/stores/<int:store_id>/',store_endpoints.get_stores_endpoint),
    path('api/stores/add/',store_endpoints.add_store_endpoint),
    path('api/stores/update/',store_endpoints.update_store_endpoint),

    path('api/products/', product_endpoints.get_products_endpoint),
    path('api/products/<int:product_id>/', product_endpoints.get_products_endpoint),
    path('api/products/store/<int:store_id>/', product_endpoints.get_products_endpoint),
    path('api/products/search/', product_endpoints.search_for_product_endpoint),
    path('api/products/search/<int:store_id>', product_endpoints.search_for_product_endpoint),
    path('api/products/add', product_endpoints.add_product_endpoint),
    path('api/products/update', product_endpoints.update_product_endpoint),
    path('api/products/update_stock', product_endpoints.update_product_stock_endpoint),
    path('api/products/remove_stock', product_endpoints.remove_stock_endpoint),
    path('api/products/add_stock', product_endpoints.add_stock_endpoint),
    path('api/products/remove', product_endpoints.remove_product_endpoint),
    path('api/products/add_image', product_endpoints.add_product_image_endpoint),
    path('api/products/images/<int:product_id>', product_endpoints.product_images_endpoint),
    path('api/products/order/<int:order_id>', product_endpoints.products_in_order_endpoint),
    path('api/products/remove_image/<int:image_id>', product_endpoints.remove_product_image_endpoint),
]
