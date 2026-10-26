from django.db import migrations


MIRO = {
    "description": (
        "A live market-intelligence workspace that makes crypto signal structure, "
        "supporting evidence, invalidation, and measured performance visible instead "
        "of presenting a black-box recommendation."
    ),
    "problem": (
        "Market dashboards can surface directional signals without explaining why a "
        "setup exists, what would invalidate it, or whether historical evidence is "
        "strong enough. Miro organizes those details into one reviewable workflow."
    ),
    "audience": (
        "Traders and market researchers who want to inspect live crypto setups and "
        "evaluate how those signals behaved over time."
    ),
    "role": (
        "Independent product design and full-stack engineering: signal workflow, "
        "Django application, data presentation, responsive interface, and operational "
        "deployment."
    ),
    "constraints": (
        "Live data can become stale or incomplete, samples can be too small to support "
        "a target, and market outcomes must not be presented as certainty. The interface "
        "also has to keep many symbols, timeframes, factors, and signal states legible."
    ),
    "decisions": (
        "Signals move through explicit lifecycle states rather than jumping straight to "
        "a trade call. The interface exposes factor alignment, confirmation counts, "
        "entry and invalidation levels, data freshness, and sample uncertainty. Separate "
        "history, analytics, backtest, news, setup, and guide views support review as "
        "well as live monitoring."
    ),
    "outcome": (
        "A deployed installable web application with live setup monitoring, annotated "
        "charts, multi-symbol screening, lifecycle history, performance analytics, "
        "backtesting, market news, documentation, and browser alerts. Performance stays "
        "explicitly measured: the product reports when a target is not statistically "
        "established instead of claiming an unverified edge."
    ),
    "lessons": (
        "For decision-support software, transparency is part of the product. Showing "
        "missing confirmations, invalidation rules, freshness, sample size, and reasons "
        "for waiting is as important as showing an active signal."
    ),
}

CAPTIONS = {
    "Screenshot_2026-09-16_1.07.27_AM.webp": (
        "Live signal workspace bringing price action, entry and invalidation levels, "
        "risk targets, and the factor-based signal overview together.",
        "Miro live market workspace with annotated chart and signal overview",
    ),
    "Screenshot_2026-09-16_1.07.48_AM.webp": (
        "Structure overlay exposing breaks of structure, changes of character, fair "
        "value gaps, order blocks, and liquidity levels on the chart.",
        "Miro chart with market-structure and liquidity overlays enabled",
    ),
    "Screenshot_2026-09-16_1.07.55_AM.webp": (
        "Live setup screener comparing symbols by direction, strength, timeframe "
        "alignment, and current lifecycle state.",
        "Miro multi-symbol live setup screener",
    ),
    "Screenshot_2026-09-16_1.08.33_AM.webp": (
        "Market pulse and news view combining major-coin performance, dominance, "
        "volume, trending assets, and sourced headlines.",
        "Miro market pulse, major coin table, trending assets, and news headlines",
    ),
}


def populate_miro(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")
    project = Project.objects.filter(title__iexact="Miro").first()
    if not project:
        return
    Project.objects.filter(pk=project.pk).update(**MIRO)
    for project_image in ProjectImage.objects.filter(project=project):
        filename = project_image.image.name.rsplit("/", 1)[-1]
        if filename in CAPTIONS:
            caption, alt_text = CAPTIONS[filename]
            ProjectImage.objects.filter(pk=project_image.pk).update(
                caption=caption,
                alt_text=alt_text,
            )


def clear_miro(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")
    project = Project.objects.filter(title__iexact="Miro").first()
    if not project:
        return
    Project.objects.filter(pk=project.pk).update(
        description="Live structure, transparent signals, and measured performance.",
        problem="",
        audience="",
        role="",
        constraints="",
        decisions="",
        outcome="",
        lessons="",
    )
    ProjectImage.objects.filter(project=project).update(caption="", alt_text="")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_project_case_studies"),
    ]

    operations = [
        migrations.RunPython(populate_miro, clear_miro),
    ]
