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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from Accounts import views as account_views, endpoints as account_endpoints
from Orders import views as endpoints as order_endpoints
from Products import views as product_views, endpoints as product_endpoints
from Stores import views as store_views, endpoints as store_endpoints


# Custom admin check
def is_admin(user):
    return user.is_authenticated and user.groups.filter(name="Admins").exists()


# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="NAME HERE API Documentation",
        default_version="v1",
        description="""This API provides seamless access to the NAME HERE system's
         functionalities for managing products, inventory, orders, and user accounts
         of both store owners and customers.""",
        contact=openapi.Contact(email="jmjohnson1578@gmail.com"),
    ),
    public=False,  # Swagger is not public; authentication required
    permission_classes=(
        permissions.IsAuthenticated,
    ),  # Only authenticated users can access
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "admin_portal/", account_views.admin_portal, name="admin_portal"
    ),  # custom admin portal for ease of use
    path("", store_views.home, name="index"),
    path("login/", account_views.login_page, name="login"),
    path("register/", account_views.register_account_page, name="register_account"),
    path("register_seller/", store_views.register_store_page, name="register_seller"),
    path("logout/", account_views.logout_view, name="logout"),
    path("home/", store_views.home, name="home"),
    path("account/", account_views.view_account, name="view_account"),
    path("my_store/", store_views.view_my_store, name="view_my_store"),
    path("add_new_product/", product_views.add_product_view, name="add_new_product"),
    path(
        "edit_product/<str:product_id>/",
        product_views.edit_product_view,
        name="edit_product",
    ),
    path(
        "view_product/<str:product_id>/",
        product_views.view_product,
        name="view_product",
    ),
    path(
        "swagger/",
        user_passes_test(is_admin)(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    path(
        "api/swagger/",
        user_passes_test(is_admin)(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    path("api/stores/", store_endpoints.get_stores_endpoint),
    path("api/stores/add/", store_endpoints.add_store_endpoint),
    path("api/stores/register/", store_endpoints.register_store_endpoint),
    path("api/stores/update/", store_endpoints.update_store_endpoint),
    path("api/stores/<int:store_id>/", store_endpoints.get_stores_endpoint),
    path("api/products/", product_endpoints.get_products_endpoint),
    path("api/products/search/", product_endpoints.search_for_product_endpoint),
    path("api/products/add/", product_endpoints.add_product_endpoint),
    path("api/products/add_image/", product_endpoints.add_product_image_endpoint),
    path("api/products/search/", product_endpoints.search_for_product_endpoint),
    path(
        "api/products/rollback_product_changes/",
        product_endpoints.rollback_product_changes_endpoint,
    ),
    path("api/products/autosave_product/", product_endpoints.autosave_product_endpoint),
    path(
        "api/products/final_save_product/",
        product_endpoints.final_save_product_endpoint,
    ),
    path("api/products/store/<int:store_id>/", product_endpoints.get_products_endpoint),
    path("api/products/<str:product_id>/", product_endpoints.get_products_endpoint),
    path("api/products/store/<int:store_id>/", product_endpoints.get_products_endpoint),
    path(
        "api/products/search/<int:store_id>/",
        product_endpoints.search_for_product_endpoint,
    ),
    path(
        "api/products/images/<str:product_id>/",
        product_endpoints.product_images_endpoint,
    ),
    path(
        "api/products/order/<int:order_id>/",
        product_endpoints.products_in_order_endpoint,
    ),
    path(
        "api/products/remove/<str:product_id>",
        product_endpoints.remove_product_endpoint,
    ),
    path(
        "api/products/remove_image/<str:image_id>/",
        product_endpoints.remove_product_image_endpoint,
    ),
    path("api/products/categories/", product_endpoints.get_categories_endpoint),
    path("api/products/subcategories/", product_endpoints.get_subcategories_endpoint),
    path(
        "api/products/topsubcategories/",
        product_endpoints.get_top_subcategories_endpoint,
    ),
    path("api/products/categories/add/", product_endpoints.add_category_endpoint),
    path("api/products/subcategories/add/", product_endpoints.add_subcategory_endpoint),
    path("api/products/categories/update/", product_endpoints.update_category_endpoint),
    path(
        "api/products/subcategories/update/",
        product_endpoints.update_subcategory_endpoint,
    ),
    path(
        "api/products/search_category/<str:category_id>/",
        product_endpoints.find_products_in_category_endpoint,
    ),
    path(
        "api/products/categories/<str:category_id>/",
        product_endpoints.get_category_endpoint,
    ),
    path(
        "api/products/subcategories/<str:subcategory_id>/",
        product_endpoints.get_subcategory_endpoint,
    ),
    path(
        "api/products/subcategories/category/<str:category_id>/",
        product_endpoints.get_subcategories_by_category_endpoint,
    ),
    path(
        "api/products/categories/remove/<str:category_id>/",
        product_endpoints.remove_category_endpoint,
    ),
    path(
        "api/products/subcategories/remove/<str:subcategory_id>/",
        product_endpoints.remove_subcategory_endpoint,
    ),
    path(
        "api/products/topsubcategories/<int:category_id>/",
        product_endpoints.get_top_subcategories_endpoint,
    ),
    path(
        "api/products/topsubcategories/update/",
        product_endpoints.update_top_subcategories_endpoint,
    ),
    path("api/accounts/", account_endpoints.get_users_endpoint),
    path("api/accounts/login/", account_endpoints.login_endpoint),
    path("api/accounts/logout/", account_endpoints.logout_endpoint),
    path(
        "api/accounts/current_user/", account_endpoints.get_current_user_info_endpoint
    ),
    path("api/accounts/customers/", account_endpoints.get_customers_endpoint),
    path("api/accounts/admins/", account_endpoints.get_admins_endpoint),
    path("api/accounts/edit_user/", account_endpoints.edit_user_endpoint),
    path(
        "api/accounts/register/", account_endpoints.register_customer_account_endpoint
    ),
    path(
        "api/accounts/username_available/",
        account_endpoints.check_username_availability_endpoint,
    ),
    path(
        "api/accounts/email_available/",
        account_endpoints.check_email_availability_endpoint,
    ),
    path(
        "api/accounts/update_profile_picture/",
        account_endpoints.update_profile_picture_endpoint,
    ),
    path("api/accounts/<str:user_id>/", account_endpoints.get_user_endpoint),
    path("api/orders/", order_endpoints.get_orders_endpoint),
    path("api/orders/add/", order_endpoints.create_order_endpoint),
    path("api/orders/update/", order_endpoints.update_order_endpoint),
    path("api/orders/<int:order_id>/", order_endpoints.get_order_endpoint),
    path("api/orders/user/<str:user_id>/", order_endpoints.get_orders_by_user_endpoint),
    path(
        "api/orders/store/<int:store_id>/", order_endpoints.get_orders_by_store_endpoint
    ),
    path(
        "retrieve_profile_picture/<str:username>",
        account_views.retrieve_profile_picture,
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
