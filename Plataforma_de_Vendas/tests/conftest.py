import pytest
from Accounts.models import CustomUser
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from Orders.models import Order
from Products.models import (
    InitialProductImage,
    InitialProductState,
    Product,
    ProductCategory,
    ProductImage,
    ProductInOrder,
    ProductSubcategory,
)
from rest_framework.test import APIClient
from Stores.models import Store


@pytest.fixture(scope="function")
def admin_group(db):
    """Fixture for the Admins group."""
    group, _ = Group.objects.get_or_create(name="Admins")
    return group


@pytest.fixture(scope="function")
def seller_group(db):
    """Fixture for the Sellers group."""
    group, _ = Group.objects.get_or_create(name="Sellers")
    return group


@pytest.fixture(scope="function")
def customer_group(db):
    """Fixture for the Customers group."""
    group, _ = Group.objects.get_or_create(name="Customers")
    return group


@pytest.fixture
def store_fixture(db):
    store = Store.objects.create(
        store_name="Test Store",
        store_description="Test Store Description",
        store_url="teststore",
        contact_email="test_contact@example.com",
    )

    return store


@pytest.fixture
def category_fixture(db):
    category = ProductCategory.objects.create(
        category_name="Test Category Name",
        category_description="Test category description",
    )

    return category


@pytest.fixture
def subcategory_fixture(db, category_fixture):
    subcategory = ProductSubcategory.objects.create(
        category=category_fixture,
        subcategory_name="Test Subcategory Name",
        subcategory_description="Test subcategory description",
    )

    return subcategory


@pytest.fixture
def mock_image():
    image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10"
    return SimpleUploadedFile("test_image.png", image_content, content_type="image/png")


@pytest.fixture
def product_fixture(db, store_fixture, subcategory_fixture, mock_image):
    product = Product.objects.create(
        store=store_fixture,
        product_name="Test Product Name",
        product_description="This is a test product description",
        properties={"test_property_1": "value1", "test_property_2": "value2"},
        prices={12: 125.0, 20: 230.0},
        subcategory=subcategory_fixture,
    )

    initial_product = InitialProductState.objects.create(
        product=product,
        store=product.store,
        product_name=product.product_name,
        product_description=product.product_description,
        properties=product.properties,
        prices=product.prices,
        original_created_at=product.created_at,
        subcategory=product.subcategory,
    )

    product_image = ProductImage.objects.create(
        product=product, image=mock_image, s3_key="test_s3_key"
    )

    InitialProductImage.objects.create(
        image=mock_image,
        product=initial_product,
        s3_key=product_image.s3_key,
        original_created_at=product_image.created_at,
    )

    return product, initial_product


# Authenticated user fixtures to use with api testing
@pytest.fixture
def admin_fixture(db):
    admin_group, _ = Group.objects.get_or_create(name="Admins")
    admin_user = CustomUser.objects.create_superuser(
        username="pytest_admin", password="password123", email="admin_email_123@example.com"
    )
    admin_user.groups.add(Group.objects.get(name="Admins"))
    admin_user.save()
    client = APIClient()
    client.force_authenticate(user=admin_user)
    assert admin_user.groups.filter(name="Admins").exists(), "Admin user is not in Admins group!"
    return admin_user, client


@pytest.fixture
def seller_fixture(db, store_fixture):
    seller_group, _ = Group.objects.get_or_create(name="Sellers")
    seller_user = CustomUser.objects.create_user(
        username="pytest_seller", password="password123", email="seller_email_123@example.com"
    )
    seller_user.groups.add(Group.objects.get(name="Sellers"))
    seller_user.store = store_fixture
    seller_user.save()
    client = APIClient()
    client.force_authenticate(user=seller_user)
    return seller_user, client


@pytest.fixture
def customer_fixture(db):
    customer_group, created = Group.objects.get_or_create(name="Customers")
    customer_user = CustomUser.objects.create_user(
        username="pytest_customer", password="password123", email="customer_email_123@example.com"
    )
    customer_user.groups.add(Group.objects.get(name="Customers"))
    customer_user.save()
    client = APIClient()
    client.force_authenticate(user=customer_user)
    return customer_user, client


# Logged in fixtures to use with view testing that
# require users to be logged in rather than authenticated
@pytest.fixture
def logged_in_admin(db):
    admin_group, _ = Group.objects.get_or_create(name="Admins")
    admin_user = CustomUser.objects.create_superuser(
        username="pytest_logged_in_admin",
        password="password123",
        email="admin_email_12345@example.com",
    )
    admin_user.groups.add(Group.objects.get(name="Admins"))
    admin_user.save()
    client = APIClient()
    client.force_login(user=admin_user)
    return admin_user, client


@pytest.fixture
def logged_in_seller(db):
    seller_group, _ = Group.objects.get_or_create(name="Sellers")
    seller_user = CustomUser.objects.create_user(
        username="pytest_logged_in_seller",
        password="password123",
        email="seller_email_12345@example.com",
    )
    seller_user.groups.add(Group.objects.get(name="Sellers"))
    seller_user.save()
    client = APIClient()
    client.force_login(user=seller_user)
    return seller_user, client


@pytest.fixture
def logged_in_customer(db):
    customer_group, _ = Group.objects.get_or_create(name="Customers")
    customer_user = CustomUser.objects.create_user(
        username="pytest_logged_in_customer",
        password="password123",
        email="customer_email_12345@example.com",
    )
    customer_user.groups.add(Group.objects.get(name="Customers"))
    customer_user.save()
    client = APIClient()
    client.force_login(user=customer_user)
    return customer_user, client


@pytest.fixture
def anonymous_client(db):
    client = APIClient()
    return client


@pytest.fixture
def random_user(db):
    user = CustomUser.objects.create_user(
        username="pytest_random_user", password="password123", email="random_user_@example.com"
    )
    return user


@pytest.fixture
def order_fixture(db, customer_fixture, store_fixture, product_fixture):
    customer_user, _ = customer_fixture
    product, _ = product_fixture
    order = Order.objects.create(
        user_id=customer_user.id,
        store_id=store_fixture.id,
        total=100.0,
        status="PENDING",
        tracking_code="123456",
    )

    ProductInOrder.objects.create(order=order, product=product, quantity=5, price=50.25)
    return order
