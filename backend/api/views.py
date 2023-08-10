from django.contrib.auth import get_user_model

# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import (
#     OpenApiExample,
#     extend_schema,
#     extend_schema_view,
# )
from rest_framework import mixins, viewsets

from api.permissions import IsAuthorBlog
from api.serializers import (
    PostSerializer,
    SubscribeParamsSerializer,
    SubscribeSerializer,
)
from api.viewsets import UserDataViewSet
from blogs.models import Post
from users.models import Subscriber

User = get_user_model()


class BlogBaseViewSet(viewsets.GenericViewSet):
    """Базовый Viewset блога пользователя."""

    def get_blog(self):
        return self.request.user.blog

    def get_queryset(self):
        return self.queryset.filter(blog=self.get_blog())


class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BlogBaseViewSet,
):
    """Посты пользователя."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorBlog]


class SubscribeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    UserDataViewSet,
):
    """Подписки пользователя."""

    serializer_class = SubscribeSerializer
    user_field = "user"
    obj_field = "author"
    obj_model = User

    def get_serializer_context(self):
        """Возвращает контекст сериализатора."""
        context = super().get_serializer_context()
        query = SubscribeParamsSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        query_params = query.validated_data
        context["posts_limit"] = query_params.get("posts_limit")
        return context

    def get_queryset(self):
        """Возвращает выборку данных по подпискам для текущего пользователя."""
        return Subscriber.objects.filter(user=self.request.user)


class NewsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Новостная лента пользователя."""

    serializer_class = PostSerializer

    def get_queryset(self):
        """Возвращает выборку данных по подпискам для текущего пользователя."""
        user = self.request.user
        subscribed = User.subscribed.through.objects.filter(user=user).values(
            "author"
        )
        return (
            Post.objects.select_related("blog")
            .filter(blog__user__in=subscribed)
            .order_by("date_create")
        )
