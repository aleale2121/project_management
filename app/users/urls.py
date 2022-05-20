from django.urls import include, path
from rest_framework_nested import routers

from users import views

app_name = "users"

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"admins", views.AdminViewSet, basename="admins")
router.register(r"users", views.UserViewSet, basename="users")
router.register(r"staffs", views.StaffViewSet, basename="staffs")
router.register(r"batches", views.BatchModelViewSet, basename="batches")
router.register(r"coordinators", views.CoordinatorModelViewSet, basename="coordinators")
student_list = views.StudentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
student_detail = views.StudentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'DELETE': 'destroy'
})
urlpatterns = [
    
    path("login/", views.CreateTokenView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('students/',student_list, name='student-list'),
    path("advisor-students/", views.advisor_groups_view, name="advisor-students"),
    path("examiner-students/", views.examiner_groups_view, name="examiner-students"),
    path('', include(router.urls)),
] 
