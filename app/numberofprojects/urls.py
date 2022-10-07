from rest_framework import routers

from .views import NumberOfVoterViewSet
router = routers.SimpleRouter(trailing_slash=False)
router.register("number_of_voters", NumberOfVoterViewSet, basename="no_of_voters")
urlpatterns = router.urls