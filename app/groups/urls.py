from django.urls import path
from rest_framework import routers

from groups import views

app_name = "groups"

router = routers.SimpleRouter()

router.register(r"groups", views.GroupsModelViewSet, basename="groups")
urlpatterns = [
  
] + router.urls