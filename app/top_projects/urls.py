from rest_framework import routers

from .views import TopProjectViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("top-projects", TopProjectViewSet, basename="top_projetcs")
urlpatterns = router.urls

