# from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

# from . import views

# app_name = "evaluations"
# urlpatterns = [
#     path("evaluations/", views.EvaluationList.as_view()),
#     path("evaluations/<int:pk>/", views.GetPutDistroyEvaluation.as_view()),
# ]
# urlpatterns = format_suffix_patterns(urlpatterns)

from django.urls import path
from rest_framework import routers

from .views import (
    StudentEvaluaionViewSet,
)

router = routers.SimpleRouter()
router.register("student/result", StudentEvaluaionViewSet, basename="students")
urlpatterns = router.urls
