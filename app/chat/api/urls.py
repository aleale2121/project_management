from rest_framework import routers

from .views import ChatViewSet,MessageViewSet
router = routers.SimpleRouter(trailing_slash=False)
router.register("chats", ChatViewSet, basename="chats")
router.register("messages", MessageViewSet, basename="messages")

urlpatterns = router.urls
