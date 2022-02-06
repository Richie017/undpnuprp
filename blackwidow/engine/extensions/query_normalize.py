__author__ = 'User'

import re

from django.db.models import Q


def normalize_query(query_strings,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    if isinstance(query_strings[0], str):
        return [[normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)][0] for query_string in query_strings]
    return query_strings


def get_query(query_string, search_fields, _in=False, range=False, **kwargs):
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    if _in:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__in" % field_name: tuple(query_string)})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        query = or_query
    elif range:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__range" % field_name: tuple(terms)})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        query = or_query
    else:
        for term in terms:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
    return query