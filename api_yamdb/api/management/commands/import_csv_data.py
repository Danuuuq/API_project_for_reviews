import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import (Category,
                            Genre,
                            Title,
                            Review,
                            Comment,
                            TitleGenre,
                            User)


class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle(self, *args, **kwargs):

        data_dir = settings.BASE_DIR / 'static' / 'data'

        self.import_data(data_dir / 'users.csv', User, ['id',
                                                        'username',
                                                        'email',
                                                        'role'])
        self.import_data(data_dir / 'category.csv', Category, ['id',
                                                               'name',
                                                               'slug'])
        self.import_data(data_dir / 'genre.csv', Genre, ['id',
                                                         'name',
                                                         'slug'])
        self.import_data(data_dir / 'titles.csv', Title, ['id',
                                                          'name',
                                                          'year',
                                                          'category_id'])
        self.import_data(data_dir / 'review.csv', Review, ['id',
                                                           'text',
                                                           'author_id',
                                                           'score',
                                                           'title_id',
                                                           'pub_date'])
        self.import_data(data_dir / 'comments.csv', Comment, ['id',
                                                              'text',
                                                              'author_id',
                                                              'review_id',
                                                              'pub_date'])
        self.import_genre_title(data_dir / 'genre_title.csv')

    def import_data(self, file_path, model, fields):
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = {field: row[field] for field in fields}
                model.objects.get_or_create(**data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded'
                                             f'data from {file_path}'))

    def import_genre_title(self, file_path):
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                TitleGenre.objects.get_or_create(
                    id=row['id'],
                    genre_id=row['genre_id'],
                    title_id=row['title_id']
                )
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded genre-title'
            f'relationships from {file_path}'))
