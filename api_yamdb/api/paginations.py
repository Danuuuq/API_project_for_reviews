from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE_PAGINATION
    order_by = ('id', )
