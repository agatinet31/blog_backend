from django.contrib.auth import get_user_model
from django.db import models
# from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Blog(models.Model):
    """Модель блога пользователя."""

    name = models.CharField(
        _("name"),
        max_length=200,
        default=_("blog"),
        help_text=_("Required. Enter name blog, please."),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    description = models.TextField(
        _("description"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")

    def __str__(self):
        """Возвращает информацию по блогу пользователя."""
        return f"Блог {self.name} (пользователь - {self.user})"
