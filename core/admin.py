from django.contrib import admin
from django.core.mail import EmailMultiAlternatives, send_mail

from security.admin_site import secure_admin_site

from .brief import BRIEF_QUESTIONS, get_questions_for_answers
from .models import BriefResponse, Photo, Post, Project, ProjectImage, PostImage
from .views import _fmt_answer, _send_brief_notification, _send_thank_you

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    fields = ("image", "caption", "alt_text", "order")
    extra = 1

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.register(Project, site=secure_admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "order", "created_at")
    list_filter = ("featured",)
    search_fields = ("title", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Project", {
            "fields": (
                "title", "slug", "description", "image", "tech_stack",
                "url", "github_url", "featured", "order",
            ),
        }),
        ("Case study", {
            "fields": (
                "problem", "audience", "role", "constraints", "decisions",
                "outcome", "lessons",
            ),
            "description": "Publish only factual details. Blank sections stay hidden.",
        }),
    )
    inlines = [ProjectImageInline]

@admin.register(Post, site=secure_admin_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "created_at")
    list_filter = ("published",)
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PostImageInline]


@admin.register(BriefResponse, site=secure_admin_site)
class BriefResponseAdmin(admin.ModelAdmin):
    list_display = ("email", "answers_preview", "admin_notified", "thank_you_sent", "created_at")
    search_fields = ("email",)
    readonly_fields = ("email", "answers_summary", "ip", "admin_notified", "thank_you_sent", "created_at")
    date_hierarchy = "created_at"
    list_per_page = 50
    actions = ("resend_emails",)

    @admin.display(description="Answers")
    def answers_preview(self, obj):
        questions = get_questions_for_answers(obj.answers)
        return " · ".join(
            f"{q['question'].split('?')[0]}: {_fmt_answer(obj.answers.get(q['id'], '—'))}"
            for q in questions
            if q["id"] in obj.answers
        )[:180]

    @admin.display(description="Full submission")
    def answers_summary(self, obj):
        questions = get_questions_for_answers(obj.answers)
        parts = [
            f"{q['question']}\n  → {_fmt_answer(obj.answers.get(q['id'], '—'))}"
            for q in questions
            if q["id"] in obj.answers
        ]
        return "\n\n".join(parts)

    @admin.display(boolean=True, description="Admin emailed")
    def admin_notified(self, obj):
        return obj.admin_notified

    @admin.display(boolean=True, description="Client thanked")
    def thank_you_sent(self, obj):
        return obj.thank_you_sent

    @admin.action(description="Resend admin notification + thank-you email")
    def resend_emails(self, request, queryset):
        for response in queryset:
            if not response.admin_notified:
                response.admin_notified = _send_brief_notification(response)
            if not response.thank_you_sent:
                response.thank_you_sent = _send_thank_you(response)
            response.save(update_fields=["admin_notified", "thank_you_sent"])
        self.message_user(request, f"Processed {queryset.count()} submission(s).")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Photo, site=secure_admin_site)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "camera", "order")
    search_fields = ("title", "location", "camera")
