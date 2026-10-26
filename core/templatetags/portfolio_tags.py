import json

import mistune
from django import template
from django.utils.safestring import mark_safe

from core.brief import (
    BRIEF_CTA,
    BRIEF_EMAIL_STEP,
    BRIEF_QUESTIONS,
    FORK_QUESTION,
    TRACK_A_QUESTIONS,
    TRACK_B_QUESTIONS,
    TRACK_OPERATIONAL,
    TRACK_PRODUCT,
)

register = template.Library()

# Shared Markdown renderer — safe mode strips raw HTML from user content.
_md = mistune.create_markdown(
    escape=True,
    plugins=["strikethrough", "table", "url"],
)


@register.filter(name="markdown", is_safe=True)
def markdown_filter(value):
    """Render a Markdown string to safe HTML."""
    if not value:
        return ""
    return mark_safe(_md(value))


@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    """Return 'active' CSS class if the current URL matches url_name."""
    request = context.get("request")
    if request is None:
        return ""
    try:
        from django.urls import resolve, reverse
        current = request.path
        target = reverse(url_name)
        # Home is only active on exact match; others match prefix.
        if url_name == "core:home":
            return "active" if current == target else ""
        return "active" if current.startswith(target) else ""
    except Exception:
        return ""


@register.simple_tag
def brief_questions_json():
    """The 90-Second Brief questionnaire as JSON for the wizard frontend."""
    return mark_safe(json.dumps({
        "fork_question": FORK_QUESTION,
        "tracks": {
            TRACK_OPERATIONAL: TRACK_A_QUESTIONS,
            TRACK_PRODUCT: TRACK_B_QUESTIONS,
        },
        "questions": BRIEF_QUESTIONS,
        "email_step": BRIEF_EMAIL_STEP,
        "cta": BRIEF_CTA,
    }))
