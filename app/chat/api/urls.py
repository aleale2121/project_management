from django.urls import path, re_path,include
from rest_framework import routers
from .views import ChatModelViewSet
from rest_framework.urlpatterns import format_suffix_patterns



from .views import (
    ChatListView,
    ChatDetailView,
    ChatCreateView,
    ChatUpdateView,
    ChatDeleteView
)
app_name = 'chat'
router = routers.SimpleRouter(trailing_slash=False)
router.register(r"channels", ChatModelViewSet, basename="channels")

urlpatterns =format_suffix_patterns( [
    path('', ChatListView.as_view()),
    path('create/', ChatCreateView.as_view()),
    path('<pk>', ChatDetailView.as_view()),
    path('<pk>/update/', ChatUpdateView.as_view()),
    path('<pk>/delete/', ChatDeleteView.as_view()),
    path("", include(router.urls)),

],
allowed=['json'],
)


