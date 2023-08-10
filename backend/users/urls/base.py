from django.urls import path
from djoser.views import UserViewSet

from api.views import SubscribeViewSet

urlpatterns = [
    path("", UserViewSet.as_view({"post": "create"}), name="users"),
    path(
        "<int:id>/", UserViewSet.as_view({"get": "retrieve"}), name="user-info"
    ),
    path(
        "me/",
        UserViewSet.as_view(
            {"get": "me", "put": "me", "patch": "me", "delete": "me"}
        ),
        name="user-me",
    ),
    path(
        "set_password/",
        UserViewSet.as_view({"post": "set_password"}),
        name="user-set-password",
    ),
    path(
        "subscriptions/",
        SubscribeViewSet.as_view({"get": "list"}),
        name="subscriptions",
    ),
    path(
        "<int:id>/subscribe/",
        SubscribeViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="subscribe",
    ),
]
