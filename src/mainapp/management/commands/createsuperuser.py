from django.core.management import BaseCommand

from mainapp.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user, _created = User.objects.get_or_create()
