import pytest
from rest_framework.test import APIClient
from Accounts.models import CustomUser
from django.contrib.auth.models import Group


@pytest.fixture
def admin_client(db):
    admin_group, created = Group.objects.get_or_create(name="Admins")
    admin_user = CustomUser.objects.create_superuser(username="pytest_admin", password="password123")
    admin_user.groups.add(Group.objects.get(name="Admins"))
    admin_user.save()
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.fixture
def seller_client(db):
    seller_group, created = Group.objects.get_or_create(name="Sellers")
    seller_user = CustomUser.objects.create_user(username="pytest_seller", password="password123")
    seller_user.groups.add(Group.objects.get(name="Sellers"))
    seller_user.save()
    client = APIClient()
    client.force_authenticate(user=seller_user)
    return client

@pytest.fixture
def customer_client(db):
    customer_group, created = Group.objects.get_or_create(name="Customers")
    customer_user = CustomUser.objects.create_user(username="pytest_customer", password="password123")
    customer_user.groups.add(Group.objects.get(name="Customers"))
    customer_user.save()
    client = APIClient()
    client.force_authenticate(user=customer_user)
    return client

@pytest.fixture
def anonymous_client(db):
    client = APIClient()
    return client