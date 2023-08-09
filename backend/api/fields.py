from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class PrimaryKey404RelatedField(serializers.PrimaryKeyRelatedField):
    """Класс первичного ключа с обработкой ошибки 404."""

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except ValidationError as exc:
            if "does_not_exist" in exc.get_codes():
                raise Http404(_("Object not found"))
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data))


class CurrentBlogDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user.blog

    def __repr__(self):
        return "%s()" % self.__class__.__name__


@extend_schema_field(OpenApiTypes.INT)
class LookupBlogRelatedField(serializers.RelatedField):
    """Lookup поле блога."""

    default_error_messages = {
        "does_not_exist": _(
            "Object with {lookup_name}={value} does not exist."
        ),
        "invalid": _("Invalid value."),
    }

    def __init__(
        self, blog=CurrentBlogDefault(), lookup_field=None, **kwargs
    ):
        assert (
            lookup_field is not None
        ), "The `lookup_field` argument is required."
        self.blog = blog
        self.lookup_field = lookup_field
        super().__init__(**kwargs)

    def get_blog(self):
        if callable(self.blog):
            if getattr(self.blog, "requires_context", False):
                return self.blog(self)
            else:
                return self.blog()
        return self.blog

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            blog = self.get_blog()
            return queryset.get(
                **{"blog": blog.pk, self.lookup_field: data}
            )
        except ObjectDoesNotExist:
            self.fail(
                "does_not_exist", lookup_name=self.lookup_field, value=data
            )
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return getattr(obj, self.lookup_field).pk
