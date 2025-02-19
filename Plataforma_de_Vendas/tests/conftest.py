import pytest
from Accounts.models import CustomUser
from django.contrib.auth.models import Group
from rest_framework.test import APIClient


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
def seller_fixture(db):
    seller_group, _ = Group.objects.get_or_create(name="Sellers")
    seller_user = CustomUser.objects.create_user(
        username="pytest_seller", password="password123", email="seller_email_123@example.com"
    )
    seller_user.groups.add(Group.objects.get(name="Sellers"))
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
