from django.urls import path

from .views import HoneypotView, TrollView

app_name = "security"

urlpatterns = [
    path("", HoneypotView.as_view(), name="honeypot"),
    path("denied/", TrollView.as_view(), name="troll"),
]