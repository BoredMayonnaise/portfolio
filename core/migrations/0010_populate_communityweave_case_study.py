from django.db import migrations


COMMUNITY_WEAVE = {
    "problem": (
        "Neighbors and barangay communities often lack a simple, dedicated way to share "
        "physical tools, offer excess backyard produce, or request mutual aid without "
        "navigating commercial algorithms, clutter, or privacy concerns on conventional social networks."
    ),
    "audience": (
        "Residents and community members across Philippine neighborhoods (including "
        "Caloocan, Quezon City, Manila, Cebu, and Davao) looking for a reliable, "
        "low-friction channel to share resources and lend a hand."
    ),
    "role": (
        "Independent product design and full-stack engineering: system architecture, "
        "Django REST API, real-time conversation flow, Vue 3 touch interface, "
        "Capacitor mobile packaging, and automated CI/CD pipeline."
    ),
    "constraints": (
        "The product needed to operate efficiently over variable mobile networks, "
        "maintain a low server resource and memory footprint, and compile into "
        "installable web (PWA) and native mobile (Android APK and iOS) packages "
        "from a unified frontend codebase."
    ),
    "decisions": (
        "Structured the backend with Django and Django REST Framework using SQLite "
        "for lightweight, low-overhead persistence. The frontend runs Vue 3 and "
        "Vite with Capacitor, offloading view rendering and map interactions to "
        "client device memory. Neighborhood interactions center around clear "
        "requests, offers, direct peer messaging, and community moderation reports."
    ),
    "outcome": (
        "A deployed, mobile-first community web app and native mobile build workflow. "
        "Features include neighborhood-scoped feeds, category filters, direct messaging "
        "between neighbors, safety reporting, automated CI/CD compiling Android APK "
        "and iOS binaries, and a dedicated mobile install portal."
    ),
    "lessons": (
        "For community utilities, clarity and accessibility matter more than feature "
        "volume. Offloading UI state and rendering to client mobile bundles keeps server "
        "requirements minimal while delivering a responsive, touch-friendly native mobile experience."
    ),
}

CAPTIONS = {
    "2.png": (
        "Neighborhood feed displaying active requests and offers scoped to local barangays.",
        "CommunityWeave neighborhood requests and offers feed",
    ),
    "3.png": (
        "Direct conversation interface connecting neighbors safely around an item or request.",
        "CommunityWeave direct neighbor conversation view",
    ),
    "4.png": (
        "Community moderation and safety reporting keeping neighbor interactions trustworthy.",
        "CommunityWeave safety reporting and moderation modal",
    ),
}


def populate_community_weave(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")
    project = Project.objects.filter(title__iexact="CommunityWeave").first()
    if not project:
        return
    Project.objects.filter(pk=project.pk).update(**COMMUNITY_WEAVE)
    for project_image in ProjectImage.objects.filter(project=project):
        filename = project_image.image.name.rsplit("/", 1)[-1]
        if filename in CAPTIONS:
            caption, alt_text = CAPTIONS[filename]
            ProjectImage.objects.filter(pk=project_image.pk).update(
                caption=caption,
                alt_text=alt_text,
            )


def clear_community_weave(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    ProjectImage = apps.get_model("core", "ProjectImage")
    project = Project.objects.filter(title__iexact="CommunityWeave").first()
    if not project:
        return
    Project.objects.filter(pk=project.pk).update(
        problem="",
        audience="",
        role="",
        constraints="",
        decisions="",
        outcome="",
        lessons="",
    )
    for project_image in ProjectImage.objects.filter(project=project):
        ProjectImage.objects.filter(pk=project_image.pk).update(
            caption="",
            alt_text="",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_populate_miro_case_study"),
    ]

    operations = [
        migrations.RunPython(populate_community_weave, clear_community_weave),
    ]
