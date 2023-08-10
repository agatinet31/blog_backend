from django.contrib.auth import get_user_model

# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import (
#     OpenApiExample,
#     extend_schema,
#     extend_schema_view,
# )
from rest_framework import mixins, viewsets

from api.permissions import IsAuthorBlog
from api.serializers import PostSerializer
from blogs.models import Post

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
