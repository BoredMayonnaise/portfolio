import random

from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import HoneypotLoginAttempt

TROLL_WORDS = [
    "nice try",
    "nope",
    "not today",
    "wrong door",
    "denied",
    "no entry",
    "try again",
    "nice thought",
    "guess again",
    "no luck",
]


@method_decorator(never_cache, name="dispatch")
class TrollView(View):
    """Redirect target for admin-honeypot attempts. Shows a random word and
    the finger-crossing figure; every hit is logged by the honeypot view."""

    def get(self, request):
        return TemplateResponse(
            request, "troll.html", {"word": random.choice(TROLL_WORDS)}
        )


@method_decorator(never_cache, name="dispatch")
class HoneypotView(View):
    """Decoy admin login. Looks identical to the real login page but logs
    every submission (bots harvesting credentials) into the DB for study.
    A successful-looking login is never granted — instead the attempt is
    redirected to the troll page."""

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def _context(self, request, error=False):
        form = AuthenticationForm(request, data=request.POST if error else None)
        if error:
            form.add_error(None, "Invalid username or password.")
        return {
            "title": "Log in",
            "app_path": request.get_full_path(),
            "site_name": "Django administration",
            "site_header": "Django administration",
            "site_title": "Django site admin",
            "site_url": "/",
            "is_popup": False,
            "form": form,
        }

    def get(self, request):
        return TemplateResponse(request, "admin/login.html", self._context(request))

    def post(self, request):
        if request.POST.get("username") or request.POST.get("password"):
            HoneypotLoginAttempt.objects.create(
                username=request.POST.get("username", "")[:200],
                password=request.POST.get("password", "")[:200],
                ip=self._client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:250],
            )
        return HttpResponseRedirect(reverse("security:troll"))
