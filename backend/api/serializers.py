from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
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
# from rest_framework.exceptions import ValidationError

from blogs.models import (
    Blog,
)

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
