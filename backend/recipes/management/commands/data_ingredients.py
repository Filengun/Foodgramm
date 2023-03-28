import csv

from django.core.management import BaseCommand
from foodgram.settings import DIR_DATA_CSV
from recipes.models import Ingredient


class Command(BaseCommand):
    '''Загружаем ингридиенты в БД'''
    def handle(self, *args, **kwargs):
        with open(
            f'{DIR_DATA_CSV}/ingredients.csv',
            newline="",
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file, fieldnames=[
                'name', 'measurement_unit'
            ])
            for row in reader:
                Ingredient.objects.update_or_create(**row)

        self.stdout.write(self.style.SUCCESS(
            'Загрузили ингредиенты'
        ))
