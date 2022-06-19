from django.urls import path
from rest_framework import routers

from .views import (EvaluaionViewSet,)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"evaluations", EvaluaionViewSet, basename="evaluations")
urlpatterns = router.urls
