from rest_framework import routers

from .views import SubmissionDeadLineViewSet

router = routers.SimpleRouter()
router.register("submission-dead-line", SubmissionDeadLineViewSet, basename="submissiondeadline")
urlpatterns = router.urls

