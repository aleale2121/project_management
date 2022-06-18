from rest_framework import routers

from .views import MarkViewSet
router = routers.SimpleRouter(trailing_slash=False)
router.register("marks", MarkViewSet, basename="marks")
urlpatterns = router.urls