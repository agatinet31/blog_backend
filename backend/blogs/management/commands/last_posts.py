from django.core.management.base import BaseCommand

from blogs.models import Post


class Command(BaseCommand):
    help = "Used to get last posts."

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="count last posts")

    def handle(self, *args, **kwargs):
        posts = list(map(str, Post.get_last_posts(kwargs["count"])))
        self.stdout.write(self.style.SUCCESS(posts))
