from django.urls import include, path
from rest_framework import routers

from api.views import NewsViewSet, PostViewSet

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register("posts", PostViewSet, basename="blog_posts")
router_v1.register("news", NewsViewSet, basename="news_posts")
urlpatterns = [
    path("", include(router_v1.urls)),
    path("users/", include("users.urls")),
    path("auth/", include("users.urls.authtoken")),
]
