from datetime import timedelta
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils._os import safe_join
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import ContactForm
from .models import ContactMessage, Photo, Post, Project

logger = logging.getLogger(__name__)

MAX_SUBMISSIONS_PER_IP = 2
RATE_WINDOW_MINUTES = 60


@require_GET
def media_file(request, path):
    """Serve a file from MEDIA_ROOT. Used in production, where WhiteNoise
    serves static files but not uploads. Path traversal is blocked via
    safe_join (resolves within MEDIA_ROOT) and an existence check."""
    try:
        full_path = safe_join(settings.MEDIA_ROOT, path)
    except (SuspiciousOperation, ValueError, TypeError):
        raise Http404
    if not Path(full_path).is_file():
        raise Http404
    return FileResponse(open(full_path, "rb"))


class HomeView(ListView):
    template_name = "core/home.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(featured=True)[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_posts"] = Post.objects.filter(published=True)[:3]
        context["photos"] = Photo.objects.all()[:6]
        return context


class ProjectListView(ListView):
    template_name = "core/project_list.html"
    context_object_name = "projects"
    queryset = Project.objects.all()


class ProjectDetailView(DetailView):
    model = Project
    template_name = "core/project_detail.html"
    context_object_name = "project"


class BlogListView(ListView):
    template_name = "core/blog_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published=True)


class PostDetailView(DetailView):
    model = Post
    template_name = "core/post_detail.html"
    context_object_name = "post"


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = "/contact/?sent=1"

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def _recent_count(self, ip):
        cutoff = timezone.now() - timedelta(minutes=RATE_WINDOW_MINUTES)
        return ContactMessage.objects.filter(
            ip=ip, created_at__gte=cutoff
        ).count()

    def post(self, request, *args, **kwargs):
        ip = self._client_ip(request)
        if self._recent_count(ip) >= MAX_SUBMISSIONS_PER_IP:
            logger.warning("Contact rate limit hit from %s", ip)
            self._notify_rate_limit(ip)
            messages.error(
                request,
                f"Rate limit reached — at most {MAX_SUBMISSIONS_PER_IP} "
                "messages per hour. Try again later.",
            )
            return HttpResponseRedirect(reverse("core:contact"))
        return super().post(request, *args, **kwargs)

    def _notify_rate_limit(self, ip):
        """Email the admin when someone trips the rate limit, at most once per
        IP per window so a flood of bot requests doesn't flood the inbox."""
        recipients = [settings.ADMIN_EMAIL] if settings.ADMIN_EMAIL else []
        if not recipients:
            return
        key = f"rate-limit-notify:{ip}"
        if cache.get(key):
            return
        cache.set(key, True, RATE_WINDOW_MINUTES * 60)
        try:
            send_mail(
                "Rate limit triggered on the contact form",
                (
                    f"IP {ip} hit the contact rate limit "
                    f"({MAX_SUBMISSIONS_PER_IP} messages/hour).\n\n"
                    "Likely a bot or someone being pushy. No action needed unless "
                    "it keeps happening."
                ),
                settings.SERVER_EMAIL,
                recipients,
            )
        except Exception:
            logger.exception("Failed to send rate-limit notification")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.ip = self._client_ip(self.request)
        message.save()
        self._send_notification(form.cleaned_data)
        messages.success(self.request, "Thanks! Your message has been sent.")
        return super().form_valid(form)

    def _send_notification(self, data):
        recipients = [settings.CONTACT_TO_EMAIL] if settings.CONTACT_TO_EMAIL else []
        if not recipients:
            logger.warning("Contact notification skipped: no CONTACT_TO_EMAIL configured.")
            return
        subject = f"New contact message from {data['name']}"
        body = (
            f"From: {data['name']} <{data['email']}>\n"
            f"IP: {self._client_ip(self.request)}\n\n"
            f"{data['message']}"
        )
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        except Exception:
            logger.exception("Failed to send contact notification email")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_sent"] = self.request.GET.get("sent") == "1"
        return context
