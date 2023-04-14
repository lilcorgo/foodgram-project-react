import json
import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            path = os.path.join(
                settings.BASE_DIR, './', 'ingredients.json',
            )
            ingredients = json.load(open(path, 'r', encoding='utf8'))
            Ingredient.objects.bulk_create(
                [Ingredient(**ingredient) for ingredient in ingredients],
                ignore_conflicts=True,
            )
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в папку data')
