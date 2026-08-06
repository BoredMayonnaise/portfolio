import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings")
django.setup()

from core.models import Photo, Post, Project

projects = [
    {
        "title": "Task Manager",
        "description": "A full-featured task management web app with user accounts, project boards, and drag-and-drop cards. Built with Django and a PostgreSQL backend.",
        "tech_stack": "Django, PostgreSQL, JavaScript",
        "url": "https://example.com/tasks",
        "github_url": "https://github.com/example/task-manager",
        "featured": True,
    },
    {
        "title": "Portfolio Site",
        "description": "This very site: a responsive portfolio and blog built from scratch with Django, SQLite, and hand-written CSS. No frameworks beyond the standard library.",
        "tech_stack": "Django, SQLite, CSS",
        "github_url": "https://github.com/example/portfolio",
        "featured": True,
    },
    {
        "title": "Weather API Dashboard",
        "description": "A small dashboard that pulls live weather data from a public API, caches responses, and renders charts. Demonstrates external API integration and caching.",
        "tech_stack": "Python, Requests, Chart.js",
        "url": "https://example.com/weather",
        "featured": True,
    },
]

posts = [
    {
        "title": "Why I chose Django for this site",
        "excerpt": "A quick look at the trade-offs behind picking a batteries-included framework.",
        "body": "Django brings an admin panel, ORM, auth, and forms out of the box, which means I can focus on content instead of boilerplate. For a personal site where I want to edit projects and posts without touching code, the built-in admin is a huge win.",
        "published": True,
    },
    {
        "title": "Getting started with class-based views",
        "excerpt": "ListView and DetailView handle the repetitive parts of CRUD.",
        "body": "Class-based views give you reusable behavior for common patterns. For example, ListView takes care of querying a model and passing the object list to the template, while DetailView resolves a slug and looks up a single record.",
        "published": True,
    },
]

photos = [
    {"title": "golden hour, quiet street", "hash": "a1b2c3d4", "location": "lisbon", "camera": "35mm f/1.4"},
    {"title": "static between towers", "hash": "e5f60718", "location": "new york", "camera": "28mm"},
    {"title": "puddle reflection", "hash": "9a0b1c2d", "location": "tokyo", "camera": "50mm"},
    {"title": "concrete geometry", "hash": "3e4f5a6b", "location": "berlin", "camera": "24mm"},
    {"title": "fog over the fjord", "hash": "7c8d9e0f", "location": "bergen", "camera": "85mm"},
    {"title": "neon after rain", "hash": "1f2e3d4c", "location": "seoul", "camera": "35mm"},
]

for p in projects:
    Project.objects.get_or_create(title=p["title"], defaults=p)

for post in posts:
    Post.objects.get_or_create(title=post["title"], defaults=post)

for photo in photos:
    Photo.objects.get_or_create(title=photo["title"], defaults=photo)

print(f"Seeded {Project.objects.count()} projects, {Post.objects.count()} posts, {Photo.objects.count()} photos.")