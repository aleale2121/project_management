from django.urls import path
from rest_framework import routers

from users import views

app_name = "users"

router = routers.SimpleRouter()

router.register(r"admins", views.AdminViewSet, basename="admins")
router.register(r"staffs", views.StaffViewSet, basename="staffs")
router.register(r"batches", views.BatchModelViewSet, basename="batches")
router.register(r"students", views.StudentViewSet, basename="students")
router.register(r"coordinators", views.CoordinatorModelViewSet, basename="coordinators")
urlpatterns = [
    path("login/", views.CreateTokenView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
] + router.urls
