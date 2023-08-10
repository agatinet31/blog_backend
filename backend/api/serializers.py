from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction

# from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from djoser.conf import settings
from djoser.serializers import (
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.fields import (  # LookupBlogRelatedField,; PrimaryKey404RelatedField,
    CurrentBlogDefault,
)
from blogs.models import Blog, Post
from users.models import Subscriber

User = get_user_model()


class AvatarMixin(serializers.Serializer):
    avatar = Base64ImageField(max_length=None, use_url=True, required=False)


class CustomUserCreateSerializer(AvatarMixin, UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "avatar",
        )

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            Blog.objects.create(
                name=f"{_('Default blog users')} {user.username}",
                user=user,
            )
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return user


class CustomUserSerializer(AvatarMixin, UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = None
        fields = UserSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "avatar",
        )


class CustomDeleteUserSerializer(serializers.Serializer):
    pass


class CustomTokenSerializer(TokenSerializer):
    id = serializers.IntegerField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    avatar = serializers.ImageField(source="user.avatar", use_url=True)

    class Meta(TokenSerializer.Meta):
        fields = TokenSerializer.Meta.fields + (
            "id",
            "first_name",
            "last_name",
            "avatar",
        )


class DefaultBlogDataSerializer(serializers.ModelSerializer):
    """Базовый сериализатор данных блога."""

    blog = serializers.HiddenField(default=CurrentBlogDefault())

    def save(self, **kwargs):
        try:
            isinstance = super().save(**kwargs)
            isinstance.full_clean()
            return isinstance
        except (IntegrityError, DjangoValidationError) as exc:
            raise ValidationError(str(exc))


class PostSerializer(DefaultBlogDataSerializer):
    """Сериализатор поста в блоге."""

    id = serializers.ReadOnlyField()
    date_create = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = ["id", "title", "text", "blog", "date_create"]


class SubscribeParamsSerializer(serializers.Serializer):
    """Сериализатор query параметров для подписок на пользователей."""

    posts_limit = serializers.IntegerField(required=False, min_value=1)


class SubscribeInfoSerializer(CustomUserSerializer):
    """Сериализатор информации по подпискам пользователей."""

    posts = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "posts",
            "count",
        )

    def get_posts(self, user):
        """Список постов пользователя."""
        posts_limit = self.context.get("posts_limit")
        posts = user.blog.posts.all()
        if posts_limit:
            posts = posts[:posts_limit]
        return PostSerializer(
            instance=posts, many=True, context=self.context
        ).data

    def get_count(self, user):
        """Возвращает количество рецептов."""
        return user.blog.posts.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор создания подписки."""

    class Meta:
        model = Subscriber
        fields = "__all__"
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscriber.objects.all(),
                fields=["user", "author"],
                message=_("The user is already following the author"),
            )
        ]

    def to_representation(self, instance):
        return SubscribeInfoSerializer(
            instance=instance.author, context=self.context
        ).data

    def validate(self, data):
        """Дополнительная проверка наличия подписки на себя."""
        if data["user"] == data["author"]:
            raise serializers.ValidationError(_("User cannot follow himself."))
        return data
