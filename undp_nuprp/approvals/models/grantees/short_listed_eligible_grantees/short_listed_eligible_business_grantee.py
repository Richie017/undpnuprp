from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import is_object_context, decorate
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.short_listed_eligible_grantee import \
    ShortListedEligibleGrantee
from undp_nuprp.reports.config.constants.pg_survey_constants import MPI_HH_RESOURCE_LIST, \
    MPI_SCORE_RELATED_QUESTION_CODES

__author__ = 'Shuvro'


@decorate(is_object_context, enable_import, route(
    route='shortlisted-eligible-business-grantee', module=ModuleEnum.Analysis,
    group='Local Economy Livelihood and Financial Inclusion',
    group_order=3, item_order=5, display_name='Short Listed Business Grantees'
))
class ShortListedEligibleBusinessGrantee(ShortListedEligibleGrantee):
    class Meta:
        app_label = 'approvals'
        proxy = True

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
            ExporterColumnConfig(column=5, column_name='CDC', property_name='render_cdc', ignore=False),
            ExporterColumnConfig(column=6, column_name='Cluster', property_name='render_cluster', ignore=False),
            ExporterColumnConfig(column=7, column_name='Ward', property_name='render_ward', ignore=False),
            ExporterColumnConfig(column=8, column_name='City', property_name='render_city', ignore=False),
            ExporterColumnConfig(column=9, column_name='Age', property_name='age', ignore=False),
            ExporterColumnConfig(column=10, column_name='Sex', property_name='gender', ignore=False),
            ExporterColumnConfig(column=11, column_name='PG Member Phone', property_name='render_pg_phone',
                                 ignore=False),
            ExporterColumnConfig(column=12, column_name='Relation with PG Member', property_name='affiliation',
                                 ignore=False),
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
            ExporterColumnConfig(column=column_no + 0,
                                 column_name='Employment status of beneficiary (Service/unemployed/business)',
                                 property_name='employment', ignore=False),
            ExporterColumnConfig(column=column_no + 1, column_name='Received from UPPR (yes/no)',
                                 property_name='other_grant_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 2, column_name='Grant type recieved from UPPR (yes/no)',
                                 property_name='other_grant_type_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 3, column_name='Received support NUPRP (yes/no)',
                                 property_name='nuprp_grant_recipient', ignore=False),
            ExporterColumnConfig(column=column_no + 4, column_name='Eligible', property_name='render_eligible',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 5, column_name='Other Grants', property_name='render_other_grants',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 6,
                                 column_name='Interested for receiving grants for business (Yes/No)',
                                 property_name='render_grant_interested', ignore=False),
            ExporterColumnConfig(column=column_no + 7, column_name='Name of business beneficiary is interested with',
                                 property_name='name_of_business', ignore=False),
            ExporterColumnConfig(column=column_no + 8, column_name='Nature of business in case of businessman',
                                 property_name='name_of_business', ignore=False),
            ExporterColumnConfig(column=column_no + 9, column_name='Geo-reference',
                                 property_name='render_geo_reference', ignore=False),
            ExporterColumnConfig(column=column_no + 10, column_name='Ethnicity', property_name='ethnicity',
                                 ignore=False),
            ExporterColumnConfig(column=column_no + 11, column_name='Female-headed HH',
                                 property_name='render_female_headed_hh', ignore=False),
            ExporterColumnConfig(column=column_no + 12, column_name='Disability Status',
                                 property_name='disability', ignore=False),
        ])

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config
