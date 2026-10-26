from datetime import timedelta
import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db import OperationalError, transaction
from django.core.exceptions import SuspiciousOperation
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import FileResponse, HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils._os import safe_join
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from .brief import BRIEF_QUESTIONS, TRACK_PRODUCT, get_questions_for_answers
from .forms import BriefForm, ContactForm
from .models import BriefResponse, ContactMessage, Photo, Post, Project

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
    response = FileResponse(
        open(full_path, "rb"),
        content_type="image/webp" if full_path.lower().endswith(".webp") else None,
    )
    if path.startswith("variants/"):
        response["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


class HomeView(ListView):
    template_name = "core/home.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_projects = list(Project.objects.all())
        context["all_projects"] = all_projects
        context["featured_projects"] = [p for p in all_projects if p.featured]
        context["latest_posts"] = Post.objects.filter(published=True)[:8]
        context["photos"] = Photo.objects.all()[:8]

        # Serialized project deck for client-side Studio Stage
        projects_payload = []
        for p in all_projects:
            projects_payload.append({
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "description": p.description,
                "problem": p.problem,
                "audience": p.audience,
                "role": p.role,
                "constraints": p.constraints,
                "decisions": p.decisions,
                "outcome": p.outcome,
                "lessons": p.lessons,
                "tech_stack": p.tech_stack,
                "tech_list": p.tech_list,
                "url": p.url,
                "github_url": p.github_url,
                "image_url": p.image.url if p.image else "",
                "detail_url": p.get_absolute_url(),
            })
        context["projects_json"] = json.dumps(projects_payload)
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
    paginate_by = 10


class PostDetailView(DetailView):
    template_name = "core/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # Drafts must 404, not leak via direct URL.
        return Post.objects.filter(published=True)


class BriefPageView(FormView):
    """The /contact/ page — a short message form and optional project brief.
    Brief submissions still use /brief/submit/ (saved to DB + notification).
    """
    template_name = "core/contact.html"
    form_class = ContactForm

    def form_invalid(self, form):
        for name, field in form.fields.items():
            if name in form.errors:
                described_by = field.widget.attrs.get("aria-describedby", "")
                field.widget.attrs["aria-describedby"] = (
                    f"{described_by} id_{name}_error".strip()
                )
        return super().form_invalid(form)

    def form_valid(self, form):
        if not form.cleaned_data.get("honeypot"):
            ip = _client_ip(self.request)
            cutoff = timezone.now() - timedelta(minutes=RATE_WINDOW_MINUTES)
            try:
                # Keep the limit check and save in one SQLite transaction.
                with transaction.atomic():
                    recent = ContactMessage.objects.filter(ip=ip, created_at__gte=cutoff)
                    if recent.count() >= MAX_SUBMISSIONS_PER_IP:
                        form.add_error(None, "Message limit reached. Please try again in an hour.")
                        response = self.form_invalid(form)
                        response.status_code = 429
                        return response
                    message = form.save(commit=False)
                    message.ip = ip
                    message.save()
            except OperationalError:
                logger.exception("Contact message could not be saved")
                form.add_error(None, "Your message could not be saved. Please try again shortly.")
                response = self.form_invalid(form)
                response.status_code = 503
                return response

            if settings.CONTACT_TO_EMAIL:
                try:
                    EmailMultiAlternatives(
                        subject="New portfolio message",
                        body=f"From: {message.name} <{message.email}>\n\n{message.message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.CONTACT_TO_EMAIL],
                        reply_to=[message.email],
                    ).send()
                except Exception:
                    logger.exception("Contact message %s saved; notification failed", message.pk)
            else:
                logger.warning("Contact message %s saved; no notification recipient configured", message.pk)

        messages.success(self.request, "Message received. I’ll review it and reply to your email.")
        return redirect(reverse("core:contact") + "#message-status")


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


@require_POST
def brief_submit(request):
    """AJAX endpoint for the 90-Second Brief modal. Returns JSON."""
    ip = _client_ip(request)
    cutoff = timezone.now() - timedelta(minutes=RATE_WINDOW_MINUTES)
    if BriefResponse.objects.filter(ip=ip, created_at__gte=cutoff).count() >= MAX_SUBMISSIONS_PER_IP:
        logger.warning("Brief rate limit hit from %s", ip)
        return JsonResponse(
            {"ok": False, "error": "Rate limit reached — try again later."},
            status=429,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid request."}, status=400)

    form = BriefForm(data=payload)
    if not form.is_valid():
        first_error = next(iter(form.errors.values()), ["Something went wrong — please try again."])
        return JsonResponse({"ok": False, "error": str(first_error[0])}, status=400)

    if form.cleaned_data.get("honeypot"):
        # Honeypot filled → almost certainly a bot. Pretend success, save nothing.
        logger.info("Brief honeypot tripped from %s", ip)
        return JsonResponse({"ok": True})

    response = BriefResponse.objects.create(
        email=form.cleaned_data["email"],
        answers=form.cleaned_data["answers"],
        ip=ip,
    )
    response.admin_notified = _send_brief_notification(response)
    response.thank_you_sent = _send_thank_you(response)
    response.save(update_fields=["admin_notified", "thank_you_sent"])
    return JsonResponse({"ok": True})


def _admin_notification_html(response, track_label, questions):
    qa_items = [
        {
            "question": q["question"],
            "answer": _fmt_answer(response.answers.get(q["id"], "—")),
        }
        for q in questions
        if q["id"] in response.answers
    ]
    context = {
        "response": response,
        "track_label": track_label,
        "qa_items": qa_items,
    }
    return render_to_string("emails/admin_notification.html", context)


def _send_brief_notification(response):
    recipients = [settings.CONTACT_TO_EMAIL] if settings.CONTACT_TO_EMAIL else []
    if not recipients:
        logger.warning("Brief notification skipped: no CONTACT_TO_EMAIL configured.")
        return False
    questions = get_questions_for_answers(response.answers)
    is_product = response.answers.get("track") == TRACK_PRODUCT
    track_label = "project brief" if is_product else "90-second brief"
    subject = f"New {track_label} from {response.email}"
    body = (
        f"From: {response.email}\n"
        f"IP: {response.ip}\n\n"
        + "\n".join(
            f"{q['question']}\n  → {_fmt_answer(response.answers.get(q['id'], '—'))}"
            for q in questions
            if q["id"] in response.answers
        )
    )
    try:
        msg = EmailMultiAlternatives(
            subject, body, settings.DEFAULT_FROM_EMAIL, recipients
        )
        msg.attach_alternative(
            _admin_notification_html(response, track_label, questions), "text/html"
        )
        msg.send()
    except Exception:
        logger.exception("Failed to send brief notification email")
        return False
    return True


def _thank_you_html(response):
    is_product = response.answers.get("track") == TRACK_PRODUCT
    if is_product:
        header_tag = "PROJECT BRIEF RECEIVED"
        h1_text = "Thank you for sharing your project."
        p_text = (
            f"Hi — your brief landed safely. I&rsquo;ll review your project details and reply to "
            f'<strong style="color:#00ff66;">{response.email}</strong> with initial thoughts '
            "and next steps shortly. If anything changes in the meantime, just respond "
            "directly to this email."
        )
    else:
        header_tag = "BRIEF RECEIVED"
        h1_text = "Thank you for sharing your problem."
        p_text = (
            f"Hi — your brief landed safely. I&rsquo;ll review your answers and reply to "
            f'<strong style="color:#00ff66;">{response.email}</strong> with an initial '
            "assessment shortly. If anything changes in the meantime, just respond "
            "directly to this email."
        )

    context = {
        "header_tag": header_tag,
        "h1_text": h1_text,
        "p_text": p_text,
        "email": response.email,
        "response": response,
    }
    return render_to_string("emails/thank_you.html", context)


def _send_thank_you(response):
    is_product = response.answers.get("track") == TRACK_PRODUCT
    if is_product:
        subject = "Thanks for sharing your project — I got your brief"
        text = (
            "Thank you for sharing your project.\n\n"
            "Your brief landed safely. I'll review your project details and reply to you "
            "shortly with initial thoughts and next steps. If anything changes in the "
            "meantime, just respond directly to this email.\n\n"
            "— Mark Ocampos"
        )
    else:
        subject = "Thanks for sharing your problem — I got your brief"
        text = (
            "Thank you for sharing your problem.\n\n"
            "Your brief landed safely. I'll review your answers and reply to you "
            "shortly with an initial assessment. If anything changes in the "
            "meantime, just respond directly to this email.\n\n"
            "— Mark Ocampos"
        )
    try:
        msg = EmailMultiAlternatives(
            subject, text, settings.DEFAULT_FROM_EMAIL, [response.email]
        )
        msg.attach_alternative(_thank_you_html(response), "text/html")
        msg.send()
    except Exception:
        logger.exception("Failed to send thank-you email to %s", response.email)
        return False
    return True


def _fmt_answer(value):
    if isinstance(value, (list, tuple)):
        return ", ".join(value)
    return value


# ---------------------------------------------------------------------------
# Sitemap & robots.txt
# ---------------------------------------------------------------------------

class SitemapView(TemplateView):
    """Dynamic XML sitemap listing all projects and published posts."""
    template_name = "sitemap.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.all()
        context["posts"] = Post.objects.filter(published=True)
        return context


@cache_control(max_age=86400)
def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /contact/\n\n"
        "Sitemap: https://markocampos.rhymvex.space/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")
