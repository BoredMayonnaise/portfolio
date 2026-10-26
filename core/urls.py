from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("media/<path:path>", views.media_file, name="media"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("blog/", views.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("contact/", views.BriefPageView.as_view(), name="contact"),
    path("brief/submit/", views.brief_submit, name="brief_submit"),
    path("sitemap.xml", views.SitemapView.as_view(), name="sitemap"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
