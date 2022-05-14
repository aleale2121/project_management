from rest_framework import routers

from .views import SubmissionDeadLineViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("submission-dead-lines", SubmissionDeadLineViewSet, basename="submissiondeadline")
urlpatterns = router.urls

