from django.contrib import admin

from security.admin_site import secure_admin_site

from .models import HoneypotLoginAttempt, RateLimitEvent


@admin.register(HoneypotLoginAttempt, site=secure_admin_site)
class HoneypotLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("ip", "username", "created_at")
    list_filter = ("created_at",)
    search_fields = ("username", "password", "ip")
    readonly_fields = ("username", "password", "ip", "user_agent", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RateLimitEvent, site=secure_admin_site)
class RateLimitEventAdmin(admin.ModelAdmin):
    list_display = ("key", "identifier", "success", "blocked", "created_at")
    list_filter = ("key", "success", "blocked")
    search_fields = ("identifier", "meta")
    readonly_fields = ("key", "identifier", "success", "blocked", "meta", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False