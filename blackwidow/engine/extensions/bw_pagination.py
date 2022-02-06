from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

__author__ = 'Tareq'


class BWPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('remaining_count',
             self.count - (self.offset + self.limit) if self.offset + self.limit < self.count else 0),
            ('next_offset', self.offset + self.limit if self.offset + self.limit < self.count else 0),
            ('current_page', int(self.offset / self.limit) + 1),
            ('total_page', int(self.count / self.limit) + (0 if (self.count % self.limit == 0) else 1)),
            ('results', data)
        ]))

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None
        try:
            url = self.request.get_full_path()
        except Exception as e:
            from blackwidow.core.models.log.error_log import ErrorLog
            ErrorLog.log(exp=e)
            url = self.request.path
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_previous_link(self):
        if self.offset <= 0:
            return None

        try:
            url = self.request.get_full_path()
        except Exception as e:
            from blackwidow.core.models.log.error_log import ErrorLog
            ErrorLog.log(exp=e)
            url = self.request.path
        url = replace_query_param(url, self.limit_query_param, self.limit)

        if self.offset - self.limit <= 0:
            return remove_query_param(url, self.offset_query_param)

        offset = self.offset - self.limit
        return replace_query_param(url, self.offset_query_param, offset)
