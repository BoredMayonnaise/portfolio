import re

from django import forms

from .brief import (
    FORK_QUESTION,
    TRACK_A_QUESTIONS,
    TRACK_B_QUESTIONS,
    TRACK_PRODUCT,
    get_questions_for_track,
)
from .models import ContactMessage

MIN_MESSAGE_WORDS = 10


class ContactForm(forms.ModelForm):
    honeypot = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 6, "aria-describedby": "message-hint"}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_message(self):
        message = self.cleaned_data["message"]
        words = [w for w in re.findall(r"[A-Za-z0-9'’\-]+", message) if w]
        if len(words) < MIN_MESSAGE_WORDS:
            raise forms.ValidationError(
                f"Please write at least {MIN_MESSAGE_WORDS} words."
            )
        return message


class BriefForm(forms.Form):
    honeypot = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.HiddenInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )
    email = forms.EmailField()
    answers = forms.JSONField(required=True)

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_answers(self):
        raw = self.cleaned_data["answers"]
        if not isinstance(raw, dict):
            raise forms.ValidationError("Invalid questionnaire answers.")

        track = raw.get("track")
        if track not in FORK_QUESTION["options"]:
            raise forms.ValidationError("Please select what brings you here today.")

        expected_questions = get_questions_for_track(track)
        expected_ids = {q["id"] for q in expected_questions}
        if set(raw.keys()) != expected_ids:
            raise forms.ValidationError("Incomplete questionnaire — please answer every question.")

        for q in expected_questions:
            answer = raw[q["id"]]
            if q.get("multi"):
                # Multi-select questions accept a non-empty list of valid options.
                if (
                    not isinstance(answer, list)
                    or not answer
                    or not all(isinstance(a, str) and a in q["options"] for a in answer)
                    or len(set(answer)) != len(answer)
                ):
                    raise forms.ValidationError(
                        "One of the answers isn't a valid option — please try again."
                    )
            elif not isinstance(answer, str) or answer not in q["options"]:
                raise forms.ValidationError(
                    "One of the answers isn't a valid option — please try again."
                )
        return raw
