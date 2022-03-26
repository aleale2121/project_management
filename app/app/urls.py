from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/v1/", include("evaluations.urls")),
    path("api/v1/", include("titles.urls")),
    path("api/v1/", include("submission_types.urls")),
    path("api/v1/", include("submissions.urls")),
    path("api/v1/", include("submission_dead_lines.urls")),
]

