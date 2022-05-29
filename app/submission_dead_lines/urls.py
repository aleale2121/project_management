from rest_framework import routers

from .views import SubmissionDeadLineViewSet, TitleSubmissionDeadLineViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("submission-dead-lines", SubmissionDeadLineViewSet, basename="submissiondeadline")
router.register("title-submission-dead-lines", TitleSubmissionDeadLineViewSet, basename="titlesubmissiondeadline")
urlpatterns = router.urls

