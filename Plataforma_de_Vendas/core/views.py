# core/views.py
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render
from django.urls.exceptions import Resolver404


def custom_404_view(request, exception):
    if isinstance(exception, Http404) and not isinstance(exception, Resolver404):
        message = str(exception)
    else:
        message = "Sorry, the page you’re looking for doesn’t exist."

    return render(request, "core/404.html", context={"message": message}, status=404)


def custom_403_view(request, exception):
    if isinstance(exception, PermissionDenied):
        message = str(exception)
    else:
        message = "You do not have permission to perform that action"
    return render(request, "core/403.html", context={"message": message}, status=403)


def custom_500_view(request):
    return render(request, "core/500.html", status=500)
