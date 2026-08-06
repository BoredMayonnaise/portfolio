import json
from datetime import timedelta

from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import RateLimitEvent


class SecureAdminSite(AdminSite):
    """AdminSite with IP-based brute-force lockout on login.

    Failures are counted per client IP within a rolling window. After
    ``LOGIN_FAIL_LIMIT`` failures in that window the IP is locked for a
    cooldown longer than the window; a successful login clears the tally.
    """

    LOGIN_FAIL_LIMIT = 5
    LOGIN_WINDOW_SECONDS = 10 * 60
    LOCKOUT_SECONDS = 15 * 60

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def _login_context(self, request, form, status=200):
        context = {
            "title": _("Log in"),
            "app_path": request.get_full_path(),
            "site_name": self.site_header,
            "site_header": self.site_header,
            "site_title": self.site_title,
            "site_url": "/",
            "has_permission": False,
            "is_popup": False,
            "form": form,
        }
        return TemplateResponse(request, self.login_template or "admin/login.html", context, status=status)

    def _is_locked(self, ip, now):
        cutoff = now - timedelta(seconds=self.LOGIN_WINDOW_SECONDS)
        events = RateLimitEvent.objects.filter(
            key="admin_login", identifier=ip, created_at__gte=cutoff
        )
        if events.filter(blocked=True).exists():
            return True
        return events.filter(success=False).count() >= self.LOGIN_FAIL_LIMIT

    def login(self, request, extra_context=None):
        if request.method == "POST":
            ip = self._client_ip(request)
            now = timezone.now()
            username = request.POST.get("username", "")

            if self._is_locked(ip, now):
                RateLimitEvent.objects.create(
                    key="admin_login",
                    identifier=ip,
                    blocked=True,
                    meta=json.dumps({"username": username}),
                    created_at=now,
                )
                form = AuthenticationForm(request, data=request.POST)
                form.add_error(
                    None,
                    _(
                        "Too many login attempts. This address is temporarily "
                        "locked for {lockout} minutes.".format(
                            lockout=self.LOCKOUT_SECONDS // 60
                        )
                    ),
                )
                return self._login_context(request, form, status=429)

            response = super().login(request, extra_context)

            if request.user.is_authenticated:
                RateLimitEvent.objects.filter(
                    key="admin_login", identifier=ip
                ).delete()
                RateLimitEvent.objects.create(
                    key="admin_login",
                    identifier=ip,
                    success=True,
                    meta=json.dumps({"username": request.user.get_username()}),
                )
            else:
                RateLimitEvent.objects.create(
                    key="admin_login",
                    identifier=ip,
                    success=False,
                    meta=json.dumps({"username": username}),
                )
            return response

        return super().login(request, extra_context)


secure_admin_site = SecureAdminSite(name="secure_admin")
secure_admin_site.login_template = "admin/login.html"