from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("groups.urls")),
    path("api/", include("submission_dead_lines.urls")),
    path("api/", include("evaluations.urls")),
    path("api/", include("semisters.urls")),
    path("api/", include("titles.urls")),
    path("api/", include("submission_types.urls")),
    path("api/", include("top_projects.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
