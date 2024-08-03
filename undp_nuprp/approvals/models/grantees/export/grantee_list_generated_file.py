import calendar
import os
import sys

from django.conf import settings
from django.db import models
from django.db.models import Max, Func, F, DateTimeField, Value, CharField, Count
from django.db.models.functions import Cast
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.models import Geography
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions import BWException
from blackwidow.engine.extensions import Clock
from blackwidow.engine.extensions.bw_titleize import bw_compress_name
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.aws_s3_config import MEDIA_DIRECTORY
from undp_nuprp.reports.config.constants.values import BATCH_SIZE

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Ziaul Haque'


class GranteeGeneratedFile(DomainEntity):
    name = models.CharField(max_length=250)
    model_name = models.CharField(max_length=250)
    last_eligible_grantee_id = models.IntegerField(default=0)
    month = models.IntegerField(default=1)
    year = models.IntegerField(default=2017)
    city = models.ForeignKey('core.Geography', null=True)
    format = models.CharField(max_length=32, blank=True)
    file = models.ForeignKey('core.FileObject', null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def default_order_by(cls):
        return ['name']

    @property
    def render_code(self):
        return self.code

    @property
    def render_file(self):
        return mark_safe('<a class="inline-link" href="' + reverse(
            ExportFileObject.get_route_name(action=ViewActionEnum.Download), kwargs={
                'pks': self.file_id}) + '">' + self.file.name + self.file.extension + '</a>')

    @classmethod
    def table_columns(cls):
        return 'render_code', 'name', 'render_file', 'format', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def generate_excel(cls, name, model, city, year, month, export_file_object=None, filename=None, columns=None,
                       id_limit=0, batch_size=BATCH_SIZE, batch_count=None, grantee_count=0):
        """
        Generate CSV format file in append mode
        :param name:
        :param model:
        :param city:
        :param year:
        :param month:
        :param export_file_object:
        :param filename:
        :param columns:
        :param id_limit:
        :param batch_size:
        :param batch_count:
        :param grantee_count:
        :return:
        """
        if batch_count is None:
            batch_count = sys.maxsize

        batch = 0
        total_handled = 0

        # to_be_handled = model.objects.order_by('pk').filter(pk__lte=id_limit).count()

        try:
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)

            dest_filename = '{}'.format(name)
            if filename:
                dest_filename = filename

            file_path = path + os.sep + dest_filename + '.csv'

            if S3_STATIC_ENABLED:
                # firstly remove the file from local directory
                if os.path.isfile(file_path):
                    os.remove(file_path)

            skip_header = False
            csv_file = open(file_path, 'w', encoding='utf-8')
            csv_file.write('\ufeff')

            last_id = 0
            while batch < batch_count:
                batch += 1
                print('Handling batch #{}: (starting from {}) {} / {}'.format(
                    batch, last_id, total_handled + batch_size, grantee_count))

                handled, last_id, report = model.build_report(
                    columns=columns, max_id=last_id, id_limit=id_limit, batch_size=BATCH_SIZE, year=year,
                    month=month, city_id=city.id if city else None
                )

                if skip_header:
                    report = report[1:]

                for _row in report:
                    row_as_str = ','.join(['"{}"'.format(_val) for _val in _row]) + '\n'
                    csv_file.write(row_as_str)
                skip_header = True

                total_handled += handled
                # if handled < batch_size means that last_id = max_recorded_id so all the grantees has been added
                # in file

                if handled < batch_size:
                    break

            csv_file.close()

            # Uploading the exported file to AMAZON S3
            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                try:
                    with open(file_path, 'rb') as content_file:
                        content = content_file.read()
                        s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                        relative_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                        AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)
                except Exception as exp:
                    ErrorLog.log(exp=exp)

                # get local file size in bytes
                local_file_size = os.path.getsize(file_path)
                local_file_last_modified = os.path.getmtime(file_path)

                # get S3 file size in bytes
                s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                s3_file_meta = AWSFileWriter.get_file_meta(file_name=s3_file_name)
                s3_file_size = s3_file_meta.content_length
                s3_file_last_modified = s3_file_meta.last_modified

                upload_attempts = 0
                while local_file_size == 0 or s3_file_size == 0 or local_file_size != s3_file_size:
                    upload_attempts += 1
                    if upload_attempts > 2:  # maximum additional tries two times
                        break

                    # create an error log entry
                    _msg = "Model Name: {0}, File Name: {1}, Source file size is {2} bytes, generated on {3}. Destination file size in S3 is {4} bytes and last modified at {5}".format(
                        cls.__name__,
                        str(dest_filename) + '.csv',
                        local_file_size,
                        Clock.get_user_local_time(local_file_last_modified * 1000).strftime("%d/%m/%Y - %I:%M %p"),
                        s3_file_size,
                        s3_file_last_modified
                    )
                    ErrorLog.log(exp=_msg)

                    try:
                        with open(file_path, 'rb') as content_file:
                            content = content_file.read()
                            s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                            relative_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                            AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)
                    except Exception as exp:
                        ErrorLog.log(exp=exp)

                    # get local file size in bytes
                    local_file_size = os.path.getsize(file_path)
                    local_file_last_modified = os.path.getmtime(file_path)

                    # get S3 file size in bytes
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                    s3_file_meta = AWSFileWriter.get_file_meta(file_name=s3_file_name)
                    s3_file_size = s3_file_meta.content_length
                    s3_file_last_modified = s3_file_meta.last_modified

            if not export_file_object:
                export_file_object = ExportFileObject()
                export_file_object.path = relative_file_path
                export_file_object.name = dest_filename
                export_file_object.file = relative_file_path
                export_file_object.extension = '.csv'
                export_file_object.organization = Organization.get_organization_from_cache()
                export_file_object.save()
            return export_file_object, last_id
        except Exception as exp:
            ErrorLog.log(exp)
        return None, None

    @classmethod
    def generate_complete_export_file(
            cls, name=None, model=None, user=None, batch_size=BATCH_SIZE, last_run_time=0, handle_upto_time=None):
        """
        Generate the whole DataSet
        :return:
        """

        model_name = model.__name__

        cities = [None]
        cities += Geography.objects.filter(type__icontains='city corporation')

        city_dict = {}
        for c in cities:
            if c:
                city_dict[c.pk] = c

        last_run_time = last_run_time.timestamp() * 1000
        handle_upto_time = handle_upto_time.timestamp() * 1000

        updated_grantees = model.objects.filter(survey_response__last_updated__gte=last_run_time,
                                                date_created__lt=handle_upto_time)
        grantee_queryset = updated_grantees.annotate(**{
            'year': Cast(Func(
                Cast(Func(
                    F('date_created') / 1000,
                    # convert millisecond timestamp to Python+PG supported second timestamp
                    function='to_timestamp'),  # convert timestamp into PG timestamp (datetime) object
                    DateTimeField()),  # assign converted field into a date-time-field
                Value('YYYY'),  # Pass the format of date field
                function='to_char'  # convert the date-time object to a date String
            ), CharField(max_length=32))
        }).annotate(**{
            'month': Cast(Func(
                Cast(Func(
                    F('date_created') / 1000,
                    # convert millisecond timestamp to Python+PG supported second timestamp
                    function='to_timestamp'),  # convert timestamp into PG timestamp (datetime) object
                    DateTimeField()),  # assign converted field into a date-time-field
                Value('MM'),  # Pass the format of date field
                function='to_char'  # convert the date-time object to a date String
            ), CharField(max_length=32))
        })

        grantee_queryset = grantee_queryset.order_by('-year', '-month').values(
            'address__geography__parent_id', 'year', 'month').annotate(grantee_count=Count('pk'))

        for distinct_combination in grantee_queryset:
            city_id = distinct_combination['address__geography__parent_id']
            year = int(distinct_combination['year'])
            month = int(distinct_combination['month'])
            grantee_count = distinct_combination['grantee_count']

            if city_id in city_dict.keys():
                city = city_dict[city_id]
            else:
                _error = BWException("No city record found for city id: {}".format(city_id))
                ErrorLog.log(exp=_error)
                continue

            print("Handling " + str(city if city else 'all cities') + ' for {} / {}'.format(month, year))
            file_name = '_'.join([name, bw_compress_name(city.name), str(year),
                                  calendar.month_name[month]]) if city else name + '_' + str(year)

            grantee_list_generated_file = cls.objects.filter(name=file_name, model_name=model_name,
                                                             city_id=city.pk if city else None,
                                                             year=year, month=month, format="Excel").first()
            if grantee_list_generated_file is None:
                grantee_list_generated_file = cls(name=file_name, model_name=model_name,
                                                  city_id=city.pk if city else None,
                                                  year=year,
                                                  month=month,
                                                  format="Excel")
                grantee_list_generated_file.created_by = user
                grantee_list_generated_file.save()

            max_handlable_grantee_id = cls.get_max_handlable_grantee_id(model=model)

            _export_file_object = grantee_list_generated_file.file

            try:
                organization = Organization.get_organization_from_cache()
                columns = model.exporter_config(organization=organization).columns.all().order_by('date_created')
            except:
                columns = None

            excel_file_obj, last_recorded_id = cls.generate_excel(
                name=file_name, model=model, city=city if city else None, year=year, month=month,
                export_file_object=_export_file_object, columns=columns,
                id_limit=max_handlable_grantee_id, batch_size=batch_size, grantee_count=grantee_count
            )
            grantee_list_generated_file.file = excel_file_obj
            grantee_list_generated_file.last_updated_by = user
            if last_recorded_id:
                grantee_list_generated_file.last_eligible_grantee_id = last_recorded_id
            grantee_list_generated_file.save()

    @classmethod
    def get_max_handlable_grantee_id(cls, model=None):
        max_grantee_id = model.objects.aggregate(Max('id'))['id__max']
        if max_grantee_id is None:
            return 0
        return int(max_grantee_id)
