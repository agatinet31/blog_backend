from django.urls import include, path
from rest_framework import routers

app_name = "api"

router_v1 = routers.DefaultRouter()
urlpatterns = [
    path("", include(router_v1.urls)),
    path("users/", include("users.urls")),
    path("auth/", include("users.urls.authtoken")),
]
