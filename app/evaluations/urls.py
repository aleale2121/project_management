from django.urls import path
from rest_framework import routers

from .views import (StudentEvaluaionViewSet,)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"evaluations", StudentEvaluaionViewSet, basename="evaluations")
urlpatterns = router.urls
