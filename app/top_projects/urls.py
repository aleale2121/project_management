from django.urls import path

from . import views

app_name = "top_projects"
urlpatterns = [
    path("top-projects", views.GetAllTopProject, name="top-projects_list"),
    path("top-projects", views.GetTopProjectByID, name="top-projects_list"),
    path("top-projects", views.CreateTopProject, name="create_top-projects"),
    path("top-projects/<int:pk>/", views.UpdateTopProject, name="update_top-projects"),
    path("top-projects/<int:pk>/", views.DeleteTopProject, name="delete_top-projects"),
]
