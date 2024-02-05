from rest_framework.pagination import LimitOffsetPagination


class PostPagination(LimitOffsetPagination):
    page_size = 10
