from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import DashboardViewSet, PostViewSet, TaskStatusViewSet, ThemeViewSet

# Criar router para API
router = DefaultRouter()
router.register(r"dashboard", DashboardViewSet, basename="dashboard")
router.register(r"themes", ThemeViewSet, basename="theme")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"tasks", TaskStatusViewSet, basename="task")

urlpatterns = [
    path("api/", include(router.urls)),
]
