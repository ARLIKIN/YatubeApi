from rest_framework.pagination import LimitOffsetPagination

from yatube_api import settings


class PostPagination(LimitOffsetPagination):
    page_size = settings.ITEM_PER_PAGE
