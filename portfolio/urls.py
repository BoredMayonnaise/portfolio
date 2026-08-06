"""URL configuration for portfolio project."""
from django.conf import settings
from django.urls import include, path

from security.admin_site import secure_admin_site

urlpatterns = [
    # Decoy login for bots; every attempt is logged and never grants access.
    path('admin/', include('security.urls')),
    # The real control panel, hidden on a secret path.
    path(settings.ADMIN_URL, secure_admin_site.urls),
    path('', include('core.urls')),
]
