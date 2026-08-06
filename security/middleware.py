from django.conf import settings

# The Django admin renderes inline <style> blocks and inline event handlers
# for its widgets (calendar, popups, filter select all, raw id links...), so a
# strict public-site CSP would break it. Keep it locked down but functional.
ADMIN_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "media-src 'self'"
)


class SecurityHeadersMiddleware:
    """Apply extra hardening headers and a relaxed CSP for the Django admin."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
            "autoplay=(), screen-wake-lock=()",
        )
        response.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        # Legacy scanner filter is recommend to be disabled outright.
        response.setdefault("X-XSS-Protection", "0")

        admin_prefix = "/" + settings.ADMIN_URL.strip("/")
        if request.path.startswith(admin_prefix):
            response["Content-Security-Policy"] = ADMIN_CSP

        return response