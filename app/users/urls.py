from django.urls import path
from rest_framework import routers

from users import views

app_name = "users"

router = routers.SimpleRouter()

router.register(r"baches", views.BatchModelViewSet, basename="batch")
router.register(r"students", views.StudentViewSet, basename="students")
urlpatterns = [
    path("create/staff/", views.StaffRegistrationView.as_view(), name="create_staff"),
    path(
        "create/student/",
        views.StudentRegistrationView.as_view(),
        name="create_student",
    ),
    # path("students/",views.StudentsOnlyView.as_view(),name="students"),
    # path("staffs/", views.StaffsOnlyView.as_view(), name="staffs"),
    path("login/", views.CreateTokenView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # path('me/', views.ManageUserView.as_view(), name='me')
] + router.urls
