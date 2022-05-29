from django.urls import include, path
from rest_framework_nested import routers

from submissions import views

app_name = "submissions"

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"submissions", views.SubmissionViewSet, basename="submissions")

urlpatterns = [
    path(r"", include(router.urls)),
]
