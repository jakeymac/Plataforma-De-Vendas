from core.views import custom_403_view, custom_404_view, custom_500_view
from django.core.exceptions import PermissionDenied
from django.http import Http404


class TestCoreViews:
    """Tests the core views."""

    def test_custom_404_view(self, anonymous_client):
        """Ensure the custom 404 view works correctly."""
        request = anonymous_client.get("/")
        request = request.wsgi_request

        response = custom_404_view(request, Http404("This product does not exist"))

        assert response.status_code == 404
        assert b"This product does not exist" in response.content

    def test_custom_403_view(self, anonymous_client):
        request = anonymous_client.get("/").wsgi_request
        response = custom_403_view(request, PermissionDenied("Test not permitted here."))

        assert response.status_code == 403
        assert b"Test not permitted here." in response.content

    def test_custom_500_view(self, anonymous_client):
        request = anonymous_client.get("/").wsgi_request
        response = custom_500_view(request)
        assert response.status_code == 500
        assert b"There was an error on our end. Please try again later" in response.content

    def test_custom_404_route(self, anonymous_client):
        response = anonymous_client.get("/test-404/")
        assert response.status_code == 404
        assert b"Testing 404" in response.content

        response = anonymous_client.get("/nonexistent-url/")
        assert response.status_code == 404
        assert (
            "Sorry, the page you’re looking for doesn’t exist.".encode("utf-8") in response.content
        )

    def test_custom_403_route(self, anonymous_client):
        response = anonymous_client.get("/test-403/")
        assert response.status_code == 403
        assert b"Testing 403" in response.content

    def test_custom_500_route(self, anonymous_client, settings):
        settings.DEBUG = False
        anonymous_client.raise_request_exception = False  # <-- prevent exception from bubbling up
        response = anonymous_client.get("/test-500/")
        assert response.status_code == 500
        assert b"There was an error on our end. Please try again later" in response.content
