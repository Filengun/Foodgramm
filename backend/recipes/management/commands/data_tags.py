from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    '''Загружаем теги в БД'''

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#1A85FF', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#D41159', 'slug': 'dinner'},
            {'name': 'Ужин', 'color': '#FFC20A', 'slug': 'supper'},
            {'name': 'Перекус', 'color': '#0ACF83', 'slug': 'snack'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)

        self.stdout.write(self.style.SUCCESS('Загрузили теги'))
