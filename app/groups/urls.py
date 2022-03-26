from django.urls import path
from rest_framework import routers

from groups import views

app_name = "groups"

router = routers.SimpleRouter()

router.register(r"groups", views.GroupsModelViewSet, basename="groups")
router.register(r"advisors", views.AdvisorModelViewSet, basename="groups-advisor")
router.register(r"examiners", views.ExaminerModelViewSet, basename="groups-examiner")

urlpatterns = [] + router.urls
