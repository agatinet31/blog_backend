from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import is_exists_user_info
from users.settings import (
    EMAIL_MAXLENGTH,
    EMAIL_MINLENGTH,
    FIRST_NAME_MAXLENGTH,
    LAST_NAME_MAXLENGTH,
    USER_ME,
    USERNAME_MAXLENGTH,
    USERNAME_MINLENGTH,
)
from users.validators import UnicodeUsernameValidator, validate_simple_name


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        username_field = "{}__iexact".format(self.model.USERNAME_FIELD)
        return self.get(**{username_field: username})


class User(AbstractUser):
    """Модель пользователей."""

    objects = CustomUserManager()

    username = models.CharField(
        _("username"),
        max_length=USERNAME_MAXLENGTH,
        unique=True,
        help_text=_(
            f"Required. {USERNAME_MINLENGTH}-{USERNAME_MAXLENGTH} characters. "
            "Letters(a-z), digits and ./+/-/_ only."
        ),
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(USERNAME_MINLENGTH),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email"),
        max_length=EMAIL_MAXLENGTH,
        unique=True,
        validators=[EmailValidator, MinLengthValidator(EMAIL_MINLENGTH)],
    )
    first_name = models.CharField(
        _("first name"),
        max_length=FIRST_NAME_MAXLENGTH,
        blank=True,
        validators=[validate_simple_name],
    )
    last_name = models.CharField(
        _("last name"),
        max_length=LAST_NAME_MAXLENGTH,
        blank=True,
        validators=[validate_simple_name],
    )
    avatar = models.ImageField(
        _("avatar"),
        blank=True,
        upload_to="users",
    )
    subscribed = models.ManyToManyField(
        "self",
        verbose_name=_("subscribed"),
        blank=True,
        symmetrical=False,
        through="Subscriber",
        through_fields=("user", "author"),
        related_name="my_subscribers",
        help_text=_("Subscribed for this user."),
    )

    class Meta(AbstractUser.Meta):
        ordering = ["username"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact=USER_ME),
                name="reserve_USER_ME",
            ),
        ]

    @property
    def is_admin(self):
        """Проверка административных прав у пользователя."""
        return self.is_staff or self.is_superuser

    def is_subscribed(self, author):
        """Проверка наличия подписок на автора."""
        return is_exists_user_info(self.subscribed, author)

    def clean(self):
        """Валидация модели."""
        if self.username.upper() == USER_ME:
            raise ValidationError(
                {
                    "username": _(
                        "The ME username is reserved. Specify another please."
                    )
                }
            )
        super().clean()

    def __str__(self):
        """Вывод данных пользователя."""
        return f"{self.username} ({self.get_full_name()}), email: {self.email}"


class Subscriber(models.Model):
    """Модель подписчика на авторов."""

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="user_subscribers",
    )
    author = models.ForeignKey(
        User,
        verbose_name=_("author"),
        on_delete=models.CASCADE,
        related_name="author_subscribers",
    )
    date_subscriber = models.DateTimeField(
        _("date subscriber"), auto_now_add=True, db_index=True
    )

    class Meta:
        """Метаданные модели подписчиков."""

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author_subscriber",
                violation_error_message=_(
                    "Subscription to the author should be unique!"
                ),
            ),
            models.CheckConstraint(
                check=~models.Q(user_id=models.F("author_id")),
                name="check_not_loop_user_author",
                violation_error_message=_(
                    "The user cannot subscribe to his blog!"
                ),
            ),
        ]
        ordering = ["-date_subscriber"]
        verbose_name = _("subscriber")
        verbose_name_plural = _("subscribers")

    def clean(self):
        """Валидация модели."""
        if self.user == self.author:
            raise ValidationError({"author": _("User cannot follow himself.")})

    def __str__(self):
        """Вывод подписчика и автора."""
        return f"{self.user.username}:{self.author.username}"
