from rest_framework import routers

from .views import SemisterViewSet
router = routers.SimpleRouter(trailing_slash=False)
router.register("semisters", SemisterViewSet, basename="semisters")
urlpatterns = router.urls