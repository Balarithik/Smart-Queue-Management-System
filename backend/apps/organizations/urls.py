from rest_framework.routers import DefaultRouter
from .views import AgentCounterViewSet, OrganizationViewSet

router = DefaultRouter()
router.register("", OrganizationViewSet, basename="organizations")
router.register("counters", AgentCounterViewSet, basename="counters")

urlpatterns = router.urls
