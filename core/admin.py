from django.contrib import admin

from security.admin_site import secure_admin_site

from .models import ContactMessage, Photo, Post, Project


@admin.register(Project, site=secure_admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "order", "created_at")
    list_filter = ("featured",)
    search_fields = ("title", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Post, site=secure_admin_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "created_at")
    list_filter = ("published",)
    search_fields = ("title", "excerpt")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage, site=secure_admin_site)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")


@admin.register(Photo, site=secure_admin_site)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "camera", "order")
    search_fields = ("title", "location", "camera")
