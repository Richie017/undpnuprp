"""
Created by tareq on 2/20/18
"""
from django.db import models

from blackwidow.core.generics.views.import_view import get_model
from blackwidow.core.models import ExporterConfig, ExporterColumnConfig
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_grantee import EligibleGrantee
from undp_nuprp.reports.config.constants.pg_survey_constants import MPI_SCORE_RELATED_QUESTION_CODES, \
    MPI_HH_RESOURCE_LIST

__author__ = 'Tareq'


class EligibleEducationGrantee(EligibleGrantee):
    school_going_count = models.IntegerField(default=0)
    disabled_count = models.IntegerField(default=0)
    diseased_count = models.IntegerField(default=0)
    school_name = models.CharField(max_length=256, blank=True)
    study_class = models.CharField(max_length=64, blank=True)

    class Meta:
        app_label = 'approvals'

    @property
    def render_diseased_count(self):
        return ''

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='Name of Beneficiary', property_name='grantee_name',
                                 ignore=False),
            ExporterColumnConfig(column=1, column_name='PG Member No', property_name='export_pg_member_number',
                                 ignore=False),
            ExporterColumnConfig(column=2, column_name='PG No', property_name='export_pg_number', ignore=False),
            ExporterColumnConfig(column=3, column_name='PG Name', property_name='render_pg_name', ignore=False),
            ExporterColumnConfig(column=4, column_name='PG Member Name', property_name='render_pg_member_name',
                                 ignore=False),
            ExporterColumnConfig(column=5, column_name='CDC', property_name='render_cdc',
                                 ignore=False),
            ExporterColumnConfig(column=6, column_name='Cluster', property_name='render_cluster', ignore=False),
            ExporterColumnConfig(column=7, column_name='Ward', property_name='render_ward', ignore=False),
            ExporterColumnConfig(column=8, column_name='City', property_name='render_city', ignore=False),
            ExporterColumnConfig(column=9, column_name='Age', property_name='age', ignore=False),
            ExporterColumnConfig(column=10, column_name='Sex', property_name='gender', ignore=False),
            ExporterColumnConfig(column=11, column_name='PG Member Phone', property_name='render_pg_phone',
                                 ignore=False),
            ExporterColumnConfig(column=12, column_name='Relation with PG Member',
                                 property_name='affiliation', ignore=False),
            ExporterColumnConfig(column=13, column_name="Household Head Name", property_name='household_head_name',
                                 ignore=False),
            ExporterColumnConfig(column=14, column_name='MPI Score', property_name='mpi_score', ignore=False),
            ExporterColumnConfig(column=15, column_name='Poverty Status', property_name='render_poverty_status',
                                 ignore=False),
            ExporterColumnConfig(column=16, column_name='Survey Date', property_name='render_survey_date',
                                 ignore=False),
        ]

        question_code_columns = []
        column_no = 17

        for mpi_score_related_question_code in MPI_SCORE_RELATED_QUESTION_CODES:
            property_name = 'render_q_code_{0}_response'.format(
                mpi_score_related_question_code.replace('.', '_'))
            # setattr(cls, property_name, property(lambda self, q_code: cls.get_question_response_func(self, q_code)))
            question_code_columns.append(ExporterColumnConfig(column=column_no,
                                                              column_name=mpi_score_related_question_code,
                                                              property_name=property_name, ignore=False))
            column_no += 1

        for mpi_hh_resource_name in MPI_HH_RESOURCE_LIST():
            property_name = 'render_resource_{0}_response'.format(mpi_hh_resource_name.lower().replace(' ', '_'))
            question_code_columns.append(ExporterColumnConfig(column=column_no,
                                                              column_name=mpi_hh_resource_name,
                                                              property_name=property_name, ignore=False))
            column_no += 1

        columns.extend(question_code_columns)

        columns.extend([
            ExporterColumnConfig(column=column_no + 0, column_name='Indegeneous Situation (Bengali/Adibasi/Bihare)',
                                 property_name='ethnicity', ignore=False),
            ExporterColumnConfig(column=column_no + 1, column_name='Received support from UPPR (yes/no)',
                                 property_name='other_grant_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 2, column_name='Grant type recieved from UPPR (yes/no)',
                                 property_name='other_grant_type_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 3, column_name='Received support NUPRP (yes/no)',
                                 property_name='nuprp_grant_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 4, column_name="Number of School Going Children",
                                 property_name='school_going_count',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 5, column_name="Number of Disabled", property_name='disabled_count',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 6, column_name="Number of Diseased",
                                 property_name='render_diseased_count',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 7, column_name='Name of School',
                                 property_name='name_of_business', ignore=False),
            ExporterColumnConfig(column=column_no + 8, column_name='Eligible', property_name='render_eligible',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 9, column_name='Other Grants',
                                 property_name='render_other_grants', ignore=False),
            ExporterColumnConfig(column=column_no + 10, column_name='Geo-reference',
                                 property_name='render_geo_reference', ignore=False),
            ExporterColumnConfig(column=column_no + 11, column_name='Ethnicity', property_name='ethnicity',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 12, column_name='Female-headed HH',
                                 property_name='render_female_headed_hh', ignore=False),
            ExporterColumnConfig(column=column_no + 13, column_name='Disability Status',
                                 property_name='disability', ignore=False),
        ])

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        return workbook

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):

        for column in columns:
            workbook.cell(row=1, column=column.column + 1).value = column.column_name

        row_number += 1

        for instance in cls.objects.using(BWDatabaseRouter.get_export_database_name()).all():
            for column in columns:
                column_value = ''
                if hasattr(instance, column.property_name):
                    column_value = str(getattr(instance, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number
