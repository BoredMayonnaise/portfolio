from django.db import models


class HoneypotLoginAttempt(models.Model):
    """Credential-ish blobs submitted by bots to the decoy admin."""

    username = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"honeypot {self.ip or '?'} @ {self.created_at:%Y-%m-%d %H:%M}"


class RateLimitEvent(models.Model):
    """Audit trail for rate-limited endpoints (admin login, contact, etc.)."""

    key = models.CharField(max_length=64, db_index=True)
    identifier = models.CharField(max_length=200, db_index=True)
    success = models.BooleanField(null=True, blank=True)
    blocked = models.BooleanField(default=False)
    meta = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["key", "identifier", "created_at"]),
        ]

    def __str__(self):
        return f"{self.key} {self.identifier} {self.created_at:%H:%M:%S}"