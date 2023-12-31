# Generated by Django 4.2.3 on 2023-08-10 18:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blogs", "0003_alter_post_options_alter_post_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="acquainted",
            field=models.ManyToManyField(
                blank=True,
                related_name="read_posts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="acquainted",
            ),
        ),
    ]
