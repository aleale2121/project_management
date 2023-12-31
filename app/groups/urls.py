from django.urls import include, path
from rest_framework_nested import routers
from groups import views

app_name = "groups"

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"groups", views.GroupsModelViewSet, basename="groups")

groups_router = routers.NestedSimpleRouter(router, r'groups', lookup='group', trailing_slash=False)
groups_router.register(r'members', views.MemberModelViewSet, basename='group-members')
groups_router.register(r'titles', views.ProjectTitleModelViewSet, basename='group-titles')
router.register(r"advisors", views.AdvisorModelViewSet, basename="groups-advisor")
router.register(r"examiners", views.ExaminerModelViewSet, basename="groups-examiner")
router.register(r"titles", views.AllProjectTitleModelViewSet, basename="all-titles")

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(groups_router.urls)),
    path("check-similarity/<int:pk>/", views.similarity_check, name="check-similarity"),
    path("approve-title/<int:pk>", views.approve_title, name="approve-title"),
    path("reject-title/<int:pk>", views.reject_title, name="reject-title"),
] 
