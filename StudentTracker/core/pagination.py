from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class HomeSessionsPagination(PageNumberPagination):
    page_size = 5   # a home widget shows a handful, not 20
    page_size_query_param = "page_size"
    max_page_size = 20
