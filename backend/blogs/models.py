from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
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


class Post(models.Model):
    """Модель поста в блоге."""

    title = models.CharField(
        _("title"),
        max_length=100,
        default=_("title"),
        db_index=True,
        help_text=_("Required. Enter name title, please."),
    )
    text = models.CharField(
        _("text"),
        max_length=140,
        blank=True,
    )
    date_create = models.DateTimeField(
        _("date create"), default=timezone.now, db_index=True
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name=_("posts"),
        verbose_name=_("blog"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("title"),
                "blog",
                name="%(app_label)s_%(class)s_title_blog",
                violation_error_message=_(
                    "The title post must be unique in blog!"
                ),
            )
        ]
        ordering = ["-date_create"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    @classmethod
    def get_last_posts(cls, count):
        """Возвращает последние посты."""
        return cls.objects.all()[:count]

    def __str__(self):
        """Возвращает информацию по посту."""
        return f"{self.name} (дата публикации - {self.user})"
