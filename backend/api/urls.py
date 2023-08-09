from django.urls import include, path
from rest_framework import routers

from api.views import (
    PostViewSet,
)

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register(
    "posts/me", PostViewSet, basename="blog_posts"
)
urlpatterns = [
    path("", include(router_v1.urls)),
    path("users/", include("users.urls")),
    path("auth/", include("users.urls.authtoken")),
]
