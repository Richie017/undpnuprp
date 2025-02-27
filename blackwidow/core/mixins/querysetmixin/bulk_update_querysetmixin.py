__author__ = 'Tareq'

import itertools

from django.db import connections, models
from django.db.models.query import QuerySet


class BulkUpdateModelManagerMixin(object):
    """
    BulkUpdateModelManager enables model manager to bulkupdate
    """
    def bulk_update(self, objs, update_fields=None,
                    exclude_fields=None, using=None, batch_size=None):
        return bulk_update(
            objs, update_fields=update_fields,
            exclude_fields=exclude_fields, using=using if using else self.db,
            batch_size=batch_size)


def _get_db_type(field, connection):
    if isinstance(field, (models.PositiveSmallIntegerField,
                          models.PositiveIntegerField)):
        # integer CHECK ("points" >= 0)'
        return field.db_type(connection).split(' ', 1)[0]

    res = field.db_type(connection)
    return res


def grouper(iterable, size):
    it = iter(iterable)
    if size <= 0:
        yield it
        return
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


def validate_fields(meta, fields):
    meta_fields = [f.attname for f in meta.fields]
    meta_fields += [f[:-3] for f in meta_fields if f.endswith('_id')]
    invalid_fields = []
    for field in fields or []:
        if field not in meta_fields:
            invalid_fields.append(field)
    if invalid_fields:
        raise TypeError(u'These fields are not present in '
                        'current meta: {}'.format(', '.join(invalid_fields)))


def bulk_update(objs, meta=None, update_fields=None, exclude_fields=None,
                using='default', batch_size=None, pk_field='pk'):
    assert batch_size is None or batch_size > 0

    # if we have a QuerySet, avoid loading objects into memory
    if isinstance(objs, QuerySet):
        if not objs.exists():
            return
        batch_size = batch_size or objs.count()
    else:
        if not objs:
            return
        batch_size = batch_size or len(objs)

    connection = connections[using]
    if meta is None:
        # TODO: account for iterables
        meta = objs[0]._meta

    if pk_field == 'pk':
        pk_field = meta.pk.name

    exclude_fields = exclude_fields or []
    update_fields = update_fields or [f.attname for f in meta.fields]
    validate_fields(meta, update_fields + exclude_fields)
    fields = [
        f for f in meta.fields
        if ((not isinstance(f, models.AutoField))
            and ((f.attname in update_fields) or
                 (f.attname.endswith('_id') and
                  f.attname[:-3] in update_fields)))]
    fields = [
        f for f in fields
        if ((f.attname not in exclude_fields) or
            (f.attname.endswith('_id') and
             f.attname[:-3] not in exclude_fields))]

    vendor = connection.vendor
    use_cast = 'mysql' not in vendor and 'sqlite' not in vendor
    if use_cast:
        case_clause_template = '"{column}" = CAST(CASE "{pkcolumn}" {{when}}'
        tail_end_template = 'END AS {type})'
    else:
        case_clause_template = '"{column}" = (CASE "{pkcolumn}" {{when}}'
        tail_end_template = 'END)'

    # String escaping in ANSI SQL is done by using double quotes (").
    # Unfortunately, this escaping method is not portable to MySQL, unless it
    # is set in ANSI compatibility mode.
    quote_mark = '"' if 'mysql' not in vendor else '`'
    case_clause_template = case_clause_template.replace('"', quote_mark)

    lenpks = 0
    for objs_batch in grouper(objs, batch_size):
        pks = []
        case_clauses = {}
        for obj in objs_batch:
            pks.append(getattr(obj, pk_field))
            for field in fields:
                column = field.column

                # Synopsis: make sure the column-specific 'case'
                # exists and then append the obj-specific values to
                # it in a tricky way (leaving ' {when}' at the end).
                # TODO?: For speed, use a list to be ''-joined later,
                # instead? Or a bytearray.
                # TODO: optimise (getitem+setitem vs. get + setitem)
                try:
                    case_clause = case_clauses[column]
                except KeyError:
                    case_clause = {
                        'sql': case_clause_template.format(
                            column=column,
                            pkcolumn=meta.get_field(pk_field).column),
                        'params': [],
                        'type': _get_db_type(field, connection=connection),
                    }
                    case_clauses[column] = case_clause

                case_clause['sql'] = (
                    case_clause['sql'].format(when="WHEN %s THEN %s {when}")
                )

                case_clause['params'].extend(
                    [getattr(obj, pk_field),
                     field.get_db_prep_value(
                         getattr(obj, field.attname), connection)])

        if pks:
            values = ', '.join(
                v['sql'].format(when=tail_end_template.format(type=v['type']))
                for v in case_clauses.values())
            parameters = [
                param
                for clause in case_clauses.values()
                for param in clause['params']]

            del case_clauses  # ... memory

            pkcolumn = meta.get_field(pk_field).column
            dbtable = '{0}{1}{0}'.format(quote_mark, meta.db_table)
            # Storytime: apparently (at least for mysql and sqlite), if a
            # non-simple parameter is added (e.g. a tuple), it is
            # processed with force_text and, accidentally, manages to
            # be a valid syntax... unless there's only one element.
            # So, to fix this, expand the ' in %s' with the parameters' string
            in_clause_sql = '({})'.format(
                ', '.join(itertools.repeat('%s', len(pks))))
            parameters.extend(pks)

            sql = (
                'UPDATE {dbtable} SET {values} WHERE {pkcolumn} '
                'in {in_clause_sql}'
                    .format(
                    dbtable=dbtable, values=values, pkcolumn=pkcolumn,
                    in_clause_sql=in_clause_sql))
            lenpks += len(pks)
            del values, pks

            connection.cursor().execute(sql, parameters)
    return lenpks
