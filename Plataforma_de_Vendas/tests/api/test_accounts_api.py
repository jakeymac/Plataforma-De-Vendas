import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
class TestGetUsersEndpoint:
    """Tests access permissions for the all-users-endpoint."""

    url = reverse("all-users-endpoint")

    def test_admin_access(self, admin_client):
        """Admin should get a 200 OK response."""
        
        response = admin_client.get(self.url)
        assert response.status_code == 200

    def test_seller_access(self, seller_client):
        """Sellers should get a 401 Unauthorized response."""
        response = seller_client.get(self.url)
        assert response.status_code == 401

    def test_unauthenticated_access(self, anonymous_client):
        """Unauthenticated users should get a 403 Forbidden response."""
        response = anonymous_client.get(self.url)
        assert response.status_code == 403
    



