import pytest
from Accounts.models import CustomUser
from django.contrib.auth.models import Group
from django.urls import reverse
from Orders.models import Order
from rest_framework.test import APIClient
from Stores.models import Store


@pytest.mark.django_db
class TestGetOrdersEndpoint:
    """ Test the get_orders_endpoint - api/orders/ - all-orders-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("all-orders-endpoint")

    def test_admin_access(self, logged_in_admin, order_fixture):
        user, client = logged_in_admin
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == order_fixture.id
        assert response.data[0]["user"] == order_fixture.user.id
        assert response.data[0]["store"] == order_fixture.store.id
        assert response.data[0]["total"] == f"{order_fixture.total:.2f}"
        assert response.data[0]["status"] == order_fixture.status

    def test_unauthorized_access(self, logged_in_seller, order_fixture):
        user, client = logged_in_seller
        response = client.get(self.url)
        assert response.status_code == 401
        assert response.data == {"error": "Unauthorized"}

    def test_unauthenticated_access(self, client, order_fixture):
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetOrderEndpoint:
    """ Test the get_order_endpoint - api/orders/<order_id>/ - order-by-id-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "order-by-id-endpoint"

    def test_admin_access(self, admin_fixture, order_fixture):
        admin_user, client = admin_fixture

        url = reverse(self.view_name, kwargs={"order_id": order_fixture.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == order_fixture.id
        assert response.data["user"] == order_fixture.user.id
        assert response.data["store"] == order_fixture.store.id
        assert response.data["total"] == f"{order_fixture.total:.2f}"
        assert response.data["status"] == order_fixture.status

    def test_seller_access(self, store_fixture, order_fixture, seller_group):
        seller_user = CustomUser.objects.create_user(
            username="pytest_logged_in_seller",
            password="password123",
            email="test_email@example.com",
            store=store_fixture,
        )
        seller_user.groups.add(seller_group.id)
        client = APIClient()
        client.force_authenticate(user=seller_user)
        
        url = reverse(self.view_name, kwargs={"order_id": order_fixture.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == order_fixture.id
        assert response.data["user"] == order_fixture.user.id
        assert response.data["store"] == order_fixture.store.id
        assert response.data["total"] == f"{order_fixture.total:.2f}"
        assert response.data["status"] == order_fixture.status

    def test_customer_access(self, customer_fixture, store_fixture):
        customer_user, client = customer_fixture
        order = Order.objects.create(
            user=customer_user, 
            store=store_fixture, 
            total=100.0,
            status="PENDING", 
            tracking_code="123456"
        )

        url = reverse(self.view_name, kwargs={"order_id": order.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == order.id
        assert response.data["user"] == order.user.id
        assert response.data["store"] == order.store.id
        assert response.data["total"] == f"{order.total:.2f}"
        assert response.data["status"] == order.status

    def test_unauthorized_access(self, logged_in_seller, order_fixture):
        user, client = logged_in_seller

        url = reverse(self.view_name, kwargs={"order_id": order_fixture.id})
        response = client.get(url)
        assert response.status_code == 401
        assert response.data == {"message": "You are not authorized to view this order"}

    def test_unauthenticated_access(self, client, order_fixture):
        url = reverse(self.view_name, kwargs={"order_id": order_fixture.id})
        response = client.get(url)

        assert response.status_code == 403

    def test_non_existent_order_id(self, logged_in_admin):
        user, client = logged_in_admin

        url = reverse(self.view_name, kwargs={"order_id": 999})
        response = client.get(url)

        assert response.status_code == 404
        assert response.data == {"message": "Order not found with the id 999"}

@pytest.mark.django_db
class TestGetOrdersByUserEndpoint:
    """ Test the get_orders_by_user_endpoint - api/orders/user/<user_id>/ - orders-by-user-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "orders-by-user-endpoint"

    def test_admin_access(self, admin_fixture, customer_fixture, order_fixture):
        admin_user, client = admin_fixture
        customer_user, _ = customer_fixture

        url = reverse(self.view_name, kwargs={"user_id": customer_user.id})
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == order_fixture.id
        assert response.data[0]["user"] == order_fixture.user.id
        assert response.data[0]["store"] == order_fixture.store.id
        assert response.data[0]["total"] == f"{order_fixture.total:.2f}"
        assert response.data[0]["status"] == order_fixture.status

    def test_customer_access(self, customer_fixture, store_fixture, order_fixture):
        customer_user, client = customer_fixture

        url = reverse(self.view_name, kwargs={"user_id": customer_user.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1

        assert response.data[0]["id"] == order_fixture.id
        assert response.data[0]["user"] == order_fixture.user.id
        assert response.data[0]["store"] == order_fixture.store.id
        assert response.data[0]["total"] == f"{order_fixture.total:.2f}"
        assert response.data[0]["status"] == order_fixture.status

    def test_unauthorized_access(self, logged_in_seller, customer_fixture):
        user, client = logged_in_seller
        customer_user, _ = customer_fixture

        url = reverse(self.view_name, kwargs={"user_id": customer_user.id})
        response = client.get(url)

        assert response.status_code == 401
        assert response.data == {"error": "You are not authorized to view these orders"}

    def test_unauthenticated_access(self, client, customer_fixture):
        customer_user, _ = customer_fixture

        url = reverse(self.view_name, kwargs={"user_id": customer_user.id})
        response = client.get(url)

        assert response.status_code == 403

    def test_nonexistent_user(self, admin_fixture):
        admin_user, client = admin_fixture

        url = reverse(self.view_name, kwargs={"user_id": 999})
        response = client.get(url)

        assert response.status_code == 404
        assert response.data == {"message": "User not found with the id 999"}


@pytest.mark.django_db
class TestGetOrdersByStoreEndpoint:
    """ Test the get_orders_by_store_endpoint - api/orders/store/<store_id>/ - orders-by-store-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "orders-by-store-endpoint"

    def test_admin_access(self, admin_fixture, store_fixture, order_fixture):
        admin_user, client = admin_fixture

        url = reverse(self.view_name, kwargs={"store_id": store_fixture.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == order_fixture.id
        assert response.data[0]["user"] == order_fixture.user.id
        assert response.data[0]["store"] == order_fixture.store.id
        assert response.data[0]["total"] == f"{order_fixture.total:.2f}"
        assert response.data[0]["status"] == order_fixture.status

    def test_seller_access(self, seller_fixture, store_fixture, order_fixture):
        seller_user, client = seller_fixture

        # Assign the store to the seller to ensure the
        # seller will be allowed to view this order
        seller_user.store = store_fixture
        seller_user.save()

        url = reverse(self.view_name, kwargs={"store_id": store_fixture.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == order_fixture.id
        assert response.data[0]["user"] == order_fixture.user.id
        assert response.data[0]["store"] == order_fixture.store.id
        assert response.data[0]["total"] == f"{order_fixture.total:.2f}"
        assert response.data[0]["status"] == order_fixture.status

    def test_unauthorized_access(self, seller_fixture, store_fixture):
        seller_user, client = seller_fixture

        seller_store = Store.objects.create(
            store_name="Seller Store",
            store_description="Seller Store Description",
            store_url="sellerstore",
            contact_email="seller_store_contact@example.com"
        )

        seller_user.store = seller_store
        seller_user.save()

        url = reverse(self.view_name, kwargs={"store_id": store_fixture.id})
        response = client.get(url)

        assert response.status_code == 401
        assert response.data == {"error": "You are not authorized to view these orders"}


    def test_unauthenticated_access(self, client, store_fixture):
        url = reverse(self.view_name, kwargs={"store_id": store_fixture.id})
        response = client.get(url)

        assert response.status_code == 403

    def test_nonexistent_store(self, admin_fixture):
        admin_user, client = admin_fixture

        url = reverse(self.view_name, kwargs={"store_id": 999})
        response = client.get(url)

        assert response.status_code == 404
        assert response.data == {"message": "Store not found with the id 999"}

@pytest.mark.django_db
class TestCreateOrderEndpoint:
    """ Test the create_order_endpoint - api/orders/create/ - create-order-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("create-order-endpoint")

    def test_authenticated_access(self, customer_fixture, store_fixture):
        customer_user, client = customer_fixture
        
        data = {
            "user": customer_user.id,
            "store": store_fixture.id,
            "total": 100.0,
            "status": "PENDING",
            "tracking_code": "123456"
        }

        response = client.post(self.url, data=data, format="json")

        assert response.status_code == 201
        assert response.data["user"] == customer_user.id
        assert response.data["store"] == store_fixture.id
        assert response.data["total"] == f"{data['total']:.2f}"
        assert response.data["status"] == data["status"]

    def test_unauthenticated_access(self, client, customer_fixture, store_fixture):
        customer_user, _ = customer_fixture

        data = {
            "user": customer_user.id,
            "store": store_fixture.id,
            "total": 100.0,
            "status": "PENDING",
            "tracking_code": "123456"
        }

        response = client.post(self.url, data=data, format="json")

        assert response.status_code == 403

    def test_unauthorized_access(self, seller_fixture, store_fixture):
        seller_user, client = seller_fixture

        data = {
            "user": seller_user.id,
            "store": store_fixture.id,
            "total": 100.0,
            "status": "PENDING",
            "tracking_code": "123456"
        }

        response = client.post(self.url, data=data, format="json")

        assert response.status_code == 401
        assert response.data == {"message": "You are not authorized to create orders"}

    def test_missing_data(self, customer_fixture):
        customer_user, client = customer_fixture

        data = {
            "user": customer_user.id,
            "total": 100.0,
            "status": "PENDING",
            "tracking_code": "123456"
        }

        response = client.post(self.url, data=data, format="json")

        assert response.status_code == 400
        assert response.data == {
            "store": ["This field is required."]
        }


@pytest.mark.django_db
class TestUpdateOrderEndpoint:
    """ Test the update_order_endpoint - api/orders/update/ - update-order-endpoint """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-order-endpoint")

    def test_admin_access(self, admin_fixture, order_fixture):
        admin_user, client = admin_fixture

        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "store": order_fixture.store.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")
        assert response.status_code == 200
        assert response.data["id"] == order_fixture.id
        assert response.data["user"] == order_fixture.user.id
        assert response.data["store"] == order_fixture.store.id
        assert response.data["total"] == f"{data['total']:.2f}"
        assert response.data["status"] == data["status"]

    def test_seller_access(self, seller_fixture, order_fixture):
        seller_user, client = seller_fixture

        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "store": order_fixture.store.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 200
        assert response.data["id"] == order_fixture.id
        assert response.data["user"] == order_fixture.user.id
        assert response.data["store"] == order_fixture.store.id
        assert response.data["total"] == f"{data['total']:.2f}"
        assert response.data["status"] == data["status"]

    def test_invalid_seller_access(self, seller_fixture, order_fixture):
        seller_user, client = seller_fixture
        new_seller_user = CustomUser.objects.create_user(
            username="new_seller",
            password="password123",
            email="new_seller@example.com",
            store=None,  # Ensure this seller is not associated with the order's store
        )
        new_seller_user.groups.add(Group.objects.get(name="Sellers"))
        new_seller_user.save()
        client = APIClient()
        client.force_authenticate(user=new_seller_user)

        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "store": order_fixture.store.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 401
        assert response.data == {"message": "You are not authorized to update this order"}

    def test_unauthorized_access(self, customer_fixture, order_fixture):
        customer_user, client = customer_fixture

        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "store": order_fixture.store.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 401
        assert response.data == {"message": "You are not authorized to update orders"}

    def test_unauthenticated_access(self, client, order_fixture):
        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "store": order_fixture.store.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 403

    def test_missing_data(self, admin_fixture, order_fixture):
        admin_user, client = admin_fixture

        data = {
            "id": order_fixture.id,
            "user": order_fixture.user.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }
    
        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 400
        assert response.data == {
            "store": ["This field is required."]
        }
    

    def test_nonexistent_order(self, admin_fixture, customer_fixture, store_fixture):
        admin_user, client = admin_fixture
        customer_user, _ = customer_fixture

        data = {
            "id": 999,
            "user": customer_user.id,
            "store": store_fixture.id,
            "total": 200.0,
            "status": "DONE",
            "tracking_code": "654321"
        }

        response = client.put(self.url, data=data, format="json")

        assert response.status_code == 404
        assert response.data == {"message": "Order not found with the id 999"}