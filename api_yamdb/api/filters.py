import django_filters
from django_filters import filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    genre = filters.CharFilter(field_name='genre__slug')
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ['category__slug', 'genre__slug', 'name', 'year']
