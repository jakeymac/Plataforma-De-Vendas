import datetime
import logging

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404

logger = logging.getLogger(__name__)


# Middleware for logging out users after a period of inactivity
class InactivityTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the timeout setting from the settings file,
        # or use default of 30 minutes (1800 seconds)
        timeout = getattr(settings, "session_inactivity_timeout", 1800)

        # If the user is actually logged in, check for inactivity
        if request.user.is_authenticated:
            last_activity = request.session.get("last_activity")
            if last_activity:
                elapsed_time = now() - datetime.datetime.fromisoformat(last_activity)
                if elapsed_time.total_seconds() > timeout:
                    logout(request)
                    request.session.flush()  # Clear the session out

            request.session["last_activity"] = now().isoformat()

        response = self.get_response(request)
        return response


class CustomExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def is_api_request(self, request):
        return request.path.startswith("/api/")

    def process_exception(self, request, exception):
        logging.error("An exception occured: ", exc_info=exception)
        if self.is_api_request(request):
            return JsonResponse(
                {"message": "An unexpected error occurred. Please try again later."}, status=500
            )
        else:
            if isinstance(exception, (Http404, PermissionDenied, SuspiciousOperation)):
                return None  # Let other handlers handle these exceptions (404 pages, etc.)
