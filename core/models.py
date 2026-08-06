import hashlib
import os

from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    tech_stack = models.CharField(
        max_length=300,
        help_text="Comma-separated list, e.g. Django, PostgreSQL, Docker",
    )
    url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "created_at")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(",") if t.strip()]

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:post_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Photo(models.Model):
    title = models.CharField(max_length=120)
    alt = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="photos/", blank=True, null=True)
    hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="Real SHA-256 of the image file, filled automatically on save.",
    )
    location = models.CharField(max_length=120, blank=True)
    camera = models.CharField(max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def _read_bytes(self):
        """Return the image bytes whether it is already stored or still in memory."""
        if not self.image:
            return b""
        try:
            if not self.image._committed and self.image.file is not None:
                src = self.image.file
                src.seek(0)
                data = src.read()
                src.seek(0)
                return data
            f = self.image.storage.open(self.image.name, "rb")
            try:
                return f.read()
            finally:
                f.close()
        except (OSError, ValueError, AttributeError):
            return b""

    def _rename_storage(self, old_name, new_name):
        try:
            src = self.image.storage.open(old_name, "rb")
            try:
                self.image.storage.save(new_name, src)
            finally:
                src.close()
        except (OSError, ValueError):
            return
        self.image.name = new_name
        if old_name != new_name:
            try:
                self.image.storage.delete(old_name)
            except OSError:
                pass

    def save(self, *args, **kwargs):
        data = self._read_bytes()
        digest = hashlib.sha256(data).hexdigest() if data else ""
        if digest:
            self.hash = digest
            ext = os.path.splitext(self.image.name)[1].lower()
            new_name = f"photos/{digest}{ext}"
            if self.image.name != new_name:
                if self.image._committed:
                    self._rename_storage(self.image.name, new_name)
                else:
                    saved = self.image.storage.save(new_name, ContentFile(data))
                    self.image.name = saved
                    self.image._committed = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title