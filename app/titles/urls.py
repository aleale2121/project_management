from rest_framework import routers

from .views import TitleViewSet

router = routers.SimpleRouter()
router.register("titles", TitleViewSet, basename="titles")
urlpatterns = router.urls

