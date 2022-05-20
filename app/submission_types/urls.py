from rest_framework import routers

from .views import SubmissionTypeViewSet
router = routers.SimpleRouter(trailing_slash=False)
router.register("submission-types", SubmissionTypeViewSet, basename="submissiontypes")
urlpatterns = router.urls