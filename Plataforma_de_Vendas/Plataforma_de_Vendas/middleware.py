import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.utils.timezone import now

# Middleware for logging out users after a period of inactivity
class InactivityTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        # Get the timeout setting from the settings file, or use default of 30 minutes (1800 seconds)
        timeout = getattr(settings, 'session_inactivity_timeout', 1800)

        # If the user is actually logged in, check for inactivity
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                elapsed_time = now() - datetime.datetime.fromisoformat(last_activity)
                if elapsed_time.total_seconds() > timeout:
                    logout(request)
                    request.session.flush() # Clear the session out
                
            request.session['last_activity'] = now().isoformat()

        response = self.get_response(request)
        return response