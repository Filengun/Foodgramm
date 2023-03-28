from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    '''передаем параметр limit'''
    page_size_query_param = "limit"
