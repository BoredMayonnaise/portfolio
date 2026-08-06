import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import ContactMessage

MIN_MESSAGE_WORDS = 10

ALLOWED_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com",
    "protonmail.com", "proton.me",
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    "yahoo.com", "yahoo.co.uk", "ymail.com",
    "icloud.com", "me.com", "mac.com",
    "aol.com",
    "gmx.com", "gmx.de", "gmx.net",
    "mail.com", "zoho.com", "fastmail.com", "fastmail.fm",
    "hey.com",
    "tutanota.com", "tuta.io",
    "yandex.com", "yandex.ru", "mail.ru", "rambler.ru",
    "web.de", "t-online.de", "freenet.de",
    "orange.fr", "free.fr", "sfr.fr",
    "btinternet.com", "virginmedia.com",
    "libero.it",
    "163.com", "126.com", "qq.com",
    "naver.com", "daum.net",
    "bol.com.br", "uol.com.br",
}


def _real_tld(domain):
    tld = domain.rsplit(".", 1)[-1]
    return tld.isalpha() and len(tld) >= 2


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        try:
            validate_email(email)
        except ValidationError as exc:
            raise forms.ValidationError("Enter a valid email address.") from exc
        domain = email.rsplit("@", 1)[-1]
        if not _real_tld(domain):
            raise forms.ValidationError("Enter a real email address (a valid domain with a TLD).")
        if domain not in ALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError(
                "Please use an email from a known provider "
                "(e.g. Gmail, Proton Mail, Outlook, Yahoo, iCloud)."
            )
        return email

    def clean_message(self):
        message = self.cleaned_data["message"]
        words = [w for w in re.findall(r"[A-Za-z0-9'’\-]+", message) if w]
        if len(words) < MIN_MESSAGE_WORDS:
            raise forms.ValidationError(
                f"Please write at least {MIN_MESSAGE_WORDS} words."
            )
        return message
