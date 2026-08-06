from django.contrib.auth.backends import ModelBackend

from axes.backends import AxesBackend


class SafeAxesBackend(AxesBackend):
    """Axes backend that still works when authenticate() is called without a
    request (e.g. management commands, django's test Client). Real HTTP logins
    always pass a request and get full brute-force protection."""

    def authenticate(self, request=None, **credentials):
        if request is None:
            return ModelBackend().authenticate(request=None, **credentials)
        return super().authenticate(request=request, **credentials)