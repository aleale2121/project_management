from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
   openapi.Info(
      title="SiTE Repository API",
      default_version='v2.1',
      description="It is a SiTE final project management system",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="yidegaait2010@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("groups.urls")),
    path("api/", include("submission_dead_lines.urls")),
    path("api/", include("evaluations.urls")),
    path("api/", include("semisters.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("api/", include("submission_types.urls")),
    path("api/", include("top_projects.urls")),
    path("api/", include("submissions.urls")),
    path('',     include('chat.urls')),
    path('api/', include('chat.api.urls'))

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore

