from django.urls import include, path
from rest_framework import routers

from api.views import AcquaintedViewSet, NewsViewSet, PostViewSet

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register("posts/me", PostViewSet, basename="blog_my_posts")
router_v1.register("news", NewsViewSet, basename="news_posts")
action_post_urlpatterns = [
    path(
        "posts/<int:id>/read",
        AcquaintedViewSet.as_view({"post": "create"}),
        name="read_posts",
    ),
]
urlpatterns = [
    path("", include(action_post_urlpatterns)),
    path("", include(router_v1.urls)),
    path("users/", include("users.urls")),
    path("auth/", include("users.urls.authtoken")),
]
