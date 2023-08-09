from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from blogs.models import Blog


@admin.register(Blog)
class CategoryAdmin(admin.ModelAdmin):
    """Конфигурация для модели Blog в админке."""

    list_display = (
        "name",
        "description",
    )
    list_filter = (
        "name",
        "description",
    )
    search_fields = ("name",)
    empty_value_display = _("empty")
