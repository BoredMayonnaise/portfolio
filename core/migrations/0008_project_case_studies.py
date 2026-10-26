from django.db import migrations, models


MICHI = {
    "description": (
        "A local-first daily practice app built around eight Japanese philosophy "
        "concepts, combining guided reflection, mindful activities, journaling, "
        "streaks, and visible progress in one calm experience."
    ),
    "problem": (
        "Mindfulness and self-improvement practices are often split across timers, "
        "habit trackers, and journals. Michi brings eight complementary practices "
        "into one daily path, making small and consistent reflection easier to sustain."
    ),
    "audience": (
        "People who want a structured, private way to build daily mindfulness, "
        "reflection, and self-improvement habits."
    ),
    "role": (
        "Independent product design and engineering: concept, interface, frontend "
        "architecture, local data model, Android packaging, and release workflow."
    ),
    "constraints": (
        "The same product needed to work across mobile, tablet, and 1440px desktop, "
        "ship as an Android APK, and keep private journal data on the user's device. "
        "The development workflow also needed to remain practical across a tablet, "
        "phone, and Chromebook."
    ),
    "decisions": (
        "Vue 3 and Capacitor keep the interface in one codebase while supporting web "
        "and Android distribution. Storage adapts by runtime: SQLite on Android and "
        "reactive localStorage on the web. Practice routes are lazy-loaded, writes are "
        "debounced, and privacy controls include a hashed PIN plus JSON export/import."
    ),
    "outcome": (
        "A working open-source product with a web preview and APK release workflow. "
        "It includes eight guided practices, more than 400 reflection prompts, local "
        "journaling, streak tracking, a responsive growth dashboard, onboarding, and "
        "data backup and restore. The project is published under the MIT License."
    ),
    "lessons": (
        "A local-first product needs platform boundaries to be explicit. Keeping the "
        "interface shared while adapting persistence and navigation to each runtime "
        "made the experience portable without treating mobile as a smaller desktop."
    ),
}

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
    "michi": {
        "mockup-export.webp": (
            "Daily dashboard combining a rotating reflection, practice progress, "
            "streak feedback, and a calm route into the day's work.",
            "Michi daily dashboard with reflection, practice progress, and streak status",
        ),
        "mockup-export_1.webp": (
            "Growth view translating completed practices into levels, activity totals, "
            "and a responsive calendar history.",
            "Michi growth dashboard with level, activity totals, and weekly calendar",
        ),
        "mockup-export_2.webp": (
            "Searchable practice library organizing all eight philosophy-based exercises "
            "by reflection, activity, and tracking.",
            "Michi practice library showing eight Japanese philosophy exercises",
        ),
    },
    "miro": {
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
    },
}


def populate_case_studies(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")

    for slug, content in (("michi", MICHI), ("miro", MIRO)):
        Project.objects.filter(slug=slug).update(**content)
        project = Project.objects.filter(slug=slug).first()
        if not project:
            continue
        captions = CAPTIONS[slug]
        for project_image in ProjectImage.objects.filter(project=project):
            filename = project_image.image.name.rsplit("/", 1)[-1]
            if filename in captions:
                caption, alt_text = captions[filename]
                ProjectImage.objects.filter(pk=project_image.pk).update(
                    caption=caption,
                    alt_text=alt_text,
                )


def clear_case_studies(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")
    blank = {
        "problem": "",
        "audience": "",
        "role": "",
        "constraints": "",
        "decisions": "",
        "outcome": "",
        "lessons": "",
    }
    Project.objects.filter(slug="michi").update(
        description=(
            "A self-evolving Japanese language learning app. Built for APK distribution "
            "with Vue.js + Capacitor — optimized for solo development on tablet, phone, "
            "and Chromebook."
        ),
        **blank,
    )
    Project.objects.filter(slug="miro").update(
        description="Live structure, transparent signals, and measured performance.",
        **blank,
    )
    case_study_ids = Project.objects.filter(slug__in=("michi", "miro")).values_list(
        "pk", flat=True
    )
    ProjectImage.objects.filter(project_id__in=case_study_ids).update(
        caption="", alt_text=""
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_responsive_image_variants"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="audience",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="constraints",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="decisions",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="lessons",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="outcome",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="problem",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="role",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="projectimage",
            name="alt_text",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="projectimage",
            name="caption",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.RunPython(populate_case_studies, clear_case_studies),
    ]
