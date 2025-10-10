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

import sys

from Accounts import endpoints as account_endpoints
from Accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from Orders import endpoints as order_endpoints
from Products import endpoints as product_endpoints
from Products import views as product_views
from rest_framework import permissions
from Stores import endpoints as store_endpoints
from Stores import views as store_views

handler404 = "core.views.custom_404_view"
handler403 = "core.views.custom_403_view"
handler500 = "core.views.custom_500_view"


# Custom admin check
def is_admin(user):
    return user.is_authenticated and user.groups.filter(name="Admins").exists()


# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Plataforma de Vendas API Documentation",
        default_version="v1",
        description="""This API provides seamless access to the Plataforma de Vendas system's
         functionalities for managing products, inventory, orders, and user accounts
         of both store owners and customers.""",
        contact=openapi.Contact(email="jmjohnson1578@gmail.com"),
    ),
    public=False,  # Swagger is not public; authentication required
    permission_classes=(permissions.IsAuthenticated,),  # Only authenticated users can access
    # TODO add a page to tell users why they can't access the swagger page, right now they just get
    # a login error
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "admin_portal/", account_views.admin_portal, name="admin_portal"
    ),  # custom admin portal for ease of use
    path("", store_views.home, name="index"),
    path("login/", account_views.login_page, name="login"),
    path("register/", account_views.register_account_page, name="register_account"),
    path("register_store/", store_views.register_store_page, name="register_store"),
    path("logout/", account_views.logout_view, name="logout"),
    path("home/", store_views.home, name="home"),
    path("account/", account_views.view_account, name="view_account"),
    path("my_store/", store_views.view_my_store, name="view_my_store"),
    path("order_dash", store_views.order_dashboard, name="order_dashboard"),
    path("add_new_product/", product_views.add_product_view, name="add_new_product"),
    path("product_search/", store_views.product_search_page, name="product_search"),
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
        "view_store/<str:store_url>/",
        store_views.view_store,
        name="view_store",
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
    ###################
    # STORE ENDPOINTS #
    ###################
    path("api/stores/", store_endpoints.get_stores_endpoint, name="all-stores-endpoint"),
    path(
        "api/stores/register/",
        store_endpoints.register_store_endpoint,
        name="register-store-endpoint",
    ),
    path(
        "api/stores/update/",
        store_endpoints.update_store_endpoint,
        name="update-store-endpoint",
    ),
    path(
        "api/stores/<str:store_id>/",
        store_endpoints.get_store_endpoint,
        name="store-by-id-endpoint",
    ),
    ######################################
    # CATEGORY AND SUBCATEGORY ENDPOINTS #
    ######################################
    path(
        "api/products/categories/",
        product_endpoints.get_categories_endpoint,
        name="all-categories-endpoint",
    ),
    path(
        "api/products/subcategories/",
        product_endpoints.get_subcategories_endpoint,
        name="all-subcategories-endpoint",
    ),
    path(
        "api/products/topsubcategories/",
        product_endpoints.get_top_subcategories_endpoint,
        name="top-subcategories-endpoint",
    ),
    path(
        "api/products/categories/add/",
        product_endpoints.add_category_endpoint,
        name="add-category-endpoint",
    ),
    path(
        "api/products/subcategories/add/",
        product_endpoints.add_subcategory_endpoint,
        name="add-subcategory-endpoint",
    ),
    path(
        "api/products/categories/update/",
        product_endpoints.update_category_endpoint,
        name="update-category-endpoint",
    ),
    path(
        "api/products/subcategories/update/",
        product_endpoints.update_subcategory_endpoint,
        name="update-subcategory-endpoint",
    ),
    path(
        "api/products/subcategories/category/<str:category_id>/",
        product_endpoints.get_subcategories_by_category_endpoint,
        name="subcategories-by-category-endpoint",
    ),
    path(
        "api/products/search_category/<str:category_id>/",
        product_endpoints.find_products_in_category_endpoint,
        name="find-products-in-category-endpoint",
    ),
    path(
        "api/products/categories/remove/<str:category_id>/",
        product_endpoints.remove_category_endpoint,
        name="remove-category-endpoint",
    ),
    path(
        "api/products/subcategories/remove/<str:subcategory_id>/",
        product_endpoints.remove_subcategory_endpoint,
        name="remove-subcategory-endpoint",
    ),
    path(
        "api/products/subcategories/<str:subcategory_id>/",
        product_endpoints.get_subcategory_endpoint,
        name="subcategory-endpoint",
    ),
    path(
        "api/products/categories/<str:category_id>/",
        product_endpoints.get_category_endpoint,
        name="category-endpoint",
    ),
    path(
        "api/products/topsubcategories/update/",
        product_endpoints.update_top_subcategories_endpoint,
        name="update-top-subcategories-endpoint",
    ),
    path(
        "api/products/topsubcategories/<str:category_id>/",
        product_endpoints.get_top_subcategories_endpoint,
        name="top-subcategories-by-category-endpoint",
    ),
    #####################
    # PRODUCT ENDPOINTS #
    #####################
    path(
        "api/products/",
        product_endpoints.get_products_endpoint,
        name="all-products-endpoint",
    ),
    path(
        "api/products/add_image/",
        product_endpoints.add_product_image_endpoint,
        name="add-product-image-endpoint",
    ),
    path(
        "api/products/add/",
        product_endpoints.add_product_endpoint,
        name="add-product-endpoint",
    ),
    path(
        "api/products/create_initial_product_state/",
        product_endpoints.create_initial_product_state_endpoint,
        name="create-initial-product-state-endpoint",
    ),
    path(
        "api/products/rollback_product_changes/",
        product_endpoints.rollback_product_changes_endpoint,
        name="rollback-product-changes-endpoint",
    ),
    path(
        "api/products/autosave_product/",
        product_endpoints.autosave_product_endpoint,
        name="autosave-product-endpoint",
    ),
    path(
        "api/products/final_save_product/",
        product_endpoints.final_save_product_endpoint,
        name="final-save-product-endpoint",
    ),
    path(
        "api/products/store/<str:store_id>/",
        product_endpoints.get_products_by_store_endpoint,
        name="products-by-store-endpoint",
    ),
    path(
        "api/products/images/<str:product_id>/",
        product_endpoints.product_images_endpoint,
        name="product-images-endpoint",  # Pulls product images by product ID
    ),
    path(
        "api/products/order/<int:order_id>/",
        product_endpoints.products_in_order_endpoint,
        name="products-in-order-endpoint",
    ),
    path(
        "api/products/remove/<str:product_id>",
        product_endpoints.remove_product_endpoint,
        name="remove-product-endpoint",
    ),
    path(
        "api/products/remove_image/<str:image_id>/",
        product_endpoints.remove_product_image_endpoint,
        name="remove-product-image-endpoint",
    ),
    path(
        "api/products/search/",
        product_endpoints.product_search_endpoint,
        name="search-products-endpoint",
    ),
    path(
        "api/products/<str:product_id>/",
        product_endpoints.get_products_endpoint,
        name="product-by-id-endpoint",
    ),
    #####################
    # ACCOUNT ENDPOINTS #
    #####################
    path("api/accounts/", account_endpoints.get_users_endpoint, name="all-users-endpoint"),
    path("api/accounts/login/", account_endpoints.login_endpoint, name="login-endpoint"),
    path(
        "api/accounts/logout/",
        account_endpoints.logout_endpoint,
        name="logout-endpoint",
    ),
    path(
        "api/accounts/current_user/",
        account_endpoints.get_current_user_info_endpoint,
        name="current-user-endpoint",
    ),
    path(
        "api/accounts/customers/",
        account_endpoints.get_customers_endpoint,
        name="all-customers-endpoint",
    ),
    path(
        "api/accounts/admins/",
        account_endpoints.get_admins_endpoint,
        name="all-admins-endpoint",
    ),
    path(
        "api/accounts/edit_user/",
        account_endpoints.edit_user_endpoint,
        name="edit-user-endpoint",
    ),
    path(
        "api/accounts/register/",
        account_endpoints.register_customer_account_endpoint,
        name="register-customer-endpoint",
    ),
    path(
        "api/accounts/username_available/",
        account_endpoints.check_username_availability_endpoint,
        name="username-availability-endpoint",
    ),
    path(
        "api/accounts/email_available/",
        account_endpoints.check_email_availability_endpoint,
        name="email-availability-endpoint",
    ),
    path(
        "api/accounts/update_profile_picture/",
        account_endpoints.update_profile_picture_endpoint,
        name="update-profile-picture-endpoint",
    ),
    path(
        "api/accounts/<str:user_id>/",
        account_endpoints.get_user_endpoint,
        name="user-by-id-endpoint",
    ),
    ###################
    # ORDER ENDPOINTS #
    ###################
    path("api/orders/", order_endpoints.get_orders_endpoint, name="all-orders-endpoint"),
    path(
        "api/orders/add/",
        order_endpoints.create_order_endpoint,
        name="create-order-endpoint",
    ),
    path(
        "api/orders/update/",
        order_endpoints.update_order_endpoint,
        name="update-order-endpoint",
    ),
    path(
        "api/orders/user/<str:user_id>/",
        order_endpoints.get_orders_by_user_endpoint,
        name="orders-by-user-endpoint",
    ),
    path(
        "api/orders/store/<str:store_id>/",
        order_endpoints.get_orders_by_store_endpoint,
        name="orders-by-store-endpoint",
    ),
    path(
        "api/orders/<int:order_id>/",
        order_endpoints.get_order_endpoint,
        name="order-by-id-endpoint",
    ),
    path(
        "api/orders/search/",
        order_endpoints.search_orders_endpoint,
        name="orders-search-endpoint",
    ),
]

# URL patterns for testing purposes only
test_url_patterns = [
    path("test-403/", lambda r: (_ for _ in ()).throw(PermissionDenied("Testing 403"))),
    path("test-404/", lambda r: (_ for _ in ()).throw(Http404("Testing 404"))),
    path("test-500/", lambda r: (_ for _ in ()).throw(Exception("Testing 500"))),
]

if "test" in sys.argv[0]:
    urlpatterns += test_url_patterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
