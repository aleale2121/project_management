from rest_framework import routers

from .views import SubmissionTypeViewSet

router = routers.SimpleRouter()
router.register("submission-types", SubmissionTypeViewSet, basename="submissiontypes")
urlpatterns = router.urls

