from django.core.management.base import BaseCommand
from django.db.models import Max

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee
from undp_nuprp.survey.models import PGMPIIndicator, QuestionResponse, PGPovertyIndex

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

    @classmethod
    def resolve_question_text_data(cls):
        queryset = QuestionResponse.objects.filter(
            question__section__survey__name="PG Member Survey Questionnaire"
        )

        # resolve question text with "refrigerator"
        queryset.filter(
            answer_text="Refrigerator",
            answer__text="Functional refrigerator"
        ).update(answer_text="Functional refrigerator")

        # resolve question text with "Smart/ Led TV"
        queryset.filter(
            answer_text="Television",
            answer__text="Smart/ Led TV"
        ).update(answer_text="Smart/ Led TV")

        # resolve question text with "Smart mobile phone"
        queryset.filter(
            answer_text="Mobile Phone",
            answer__text="Smart mobile phone"
        ).update(answer_text="Smart mobile phone")

        # resolve question text with "Earth/sand/semi pucca floor"
        queryset.filter(
            answer_text="Earth/sand",
            answer__text="Earth/sand/semi pucca floor"
        ).update(answer_text="Earth/sand/semi pucca floor")

    @classmethod
    def delete_poverty_index(cls):
        # delete existing poverty index with index no - 10
        queryset = PGPovertyIndex.objects.filter(index_no=10)
        for i in range(1, 110):
            q = queryset.filter(pk__in=queryset.values_list('pk', flat=True)[:5000])
            print(i, q.delete())

    @classmethod
    def recalculate_mpi_score_data(cls, last_processed_id=0, response_id=None):
        indicator_queryset = PGMPIIndicator.objects.filter(
            pk__gt=last_processed_id
        ).order_by('pk')

        if response_id:
            indicator_queryset = indicator_queryset.filter(
                survey_response_id=response_id
            ).order_by('pk')

        offset = 0
        limit = 1000

        max_id = indicator_queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0

        while max_processed_id < max_id:
            indicators = indicator_queryset[offset:limit]
            updatable_indicator_items = []
            updatable_business_items = []
            updatable_apprenticeship_items = []
            updatable_drop_out_items = []
            updatable_early_marriage_items = []
            creatable_poverty_indices = []
            for indicator_obj in indicators:
                response_obj = indicator_obj.survey_response
                respondent_client = response_obj.respondent_client
                max_processed_id = indicator_obj.id

                # calculate mpi score
                mpi_indicator, indices = PGMPIIndicator.get_mpi_indicator_object_for_survey_response(
                    response=response_obj,
                    organization_id=indicator_obj.organization_id,
                    poverty_indices=[]
                )
                mpi_score = round(mpi_indicator.mpi_score, 2)
                mpi_indicator.mpi_score = mpi_score
                updatable_indicator_items.append(mpi_indicator)
                # mpi_indicator.save()

                for poverty_index in indices:
                    if poverty_index.index_no == 10:
                        creatable_poverty_indices.append(poverty_index)

                # Update Eligible Grantees
                business_queryset = EligibleBusinessGrantee.objects.filter(
                    pg_member=respondent_client
                )

                apprenticeship_queryset = EligibleApprenticeshipGrantee.objects.filter(
                    pg_member=respondent_client
                )

                drop_out_queryset = EligibleEducationDropOutGrantee.objects.filter(
                    pg_member=respondent_client
                )

                early_marriage_queryset = EligibleEducationEarlyMarriageGrantee.objects.filter(
                    pg_member=respondent_client
                )

                for business_item in business_queryset:
                    business_item.mpi_score = mpi_score
                    if business_item.is_eligible and mpi_score < 20:
                        business_item.is_eligible = False
                    updatable_business_items.append(business_item)

                    if len(updatable_business_items) == 1000:
                        print("processing {} {} items.".format(
                            len(updatable_business_items), EligibleBusinessGrantee.__name__))
                        EligibleBusinessGrantee.objects.bulk_update(
                            objs=updatable_business_items,
                            using=BWDatabaseRouter.get_write_database_name()
                        )
                        updatable_business_items = []
                        print("processed.")

                for apprenticeship_item in apprenticeship_queryset:
                    apprenticeship_item.mpi_score = mpi_score
                    if apprenticeship_item.is_eligible and mpi_score < 20:
                        apprenticeship_item.is_eligible = False
                    updatable_apprenticeship_items.append(apprenticeship_item)

                    if len(updatable_apprenticeship_items) == 1000:
                        print("processing {} {} items.".format(
                            len(updatable_apprenticeship_items), EligibleApprenticeshipGrantee.__name__))
                        EligibleApprenticeshipGrantee.objects.bulk_update(
                            objs=updatable_apprenticeship_items,
                            using=BWDatabaseRouter.get_write_database_name()
                        )
                        updatable_apprenticeship_items = []
                        print("processed.")

                for drop_out_item in drop_out_queryset:
                    drop_out_item.mpi_score = mpi_score
                    if drop_out_item.is_eligible and mpi_score < 20:
                        drop_out_item.is_eligible = False
                    updatable_drop_out_items.append(drop_out_item)

                    if len(updatable_drop_out_items) == 1000:
                        print("processing {} {} items.".format(
                            len(updatable_drop_out_items), EligibleEducationDropOutGrantee.__name__))
                        EligibleEducationDropOutGrantee.objects.bulk_update(
                            objs=updatable_drop_out_items,
                            using=BWDatabaseRouter.get_write_database_name()
                        )
                        updatable_drop_out_items = []
                        print("processed.")

                for early_marriage_item in early_marriage_queryset:
                    early_marriage_item.mpi_score = mpi_score
                    if early_marriage_item.is_eligible and mpi_score < 20:
                        early_marriage_item.is_eligible = False
                    updatable_early_marriage_items.append(early_marriage_item)

                    if len(updatable_early_marriage_items) == 1000:
                        print("processing {} {} items.".format(
                            len(updatable_early_marriage_items), EligibleEducationEarlyMarriageGrantee.__name__))
                        EligibleEducationEarlyMarriageGrantee.objects.bulk_update(
                            objs=updatable_early_marriage_items,
                            using=BWDatabaseRouter.get_write_database_name()
                        )
                        updatable_early_marriage_items = []
                        print("processed.")

                print("PG MPI Indicator ID: {0}".format(indicator_obj.pk))

            if len(updatable_indicator_items) > 0:
                print("processing {} {} items.".format(len(updatable_indicator_items), PGMPIIndicator.__name__))
                PGMPIIndicator.objects.bulk_update(
                    objs=updatable_indicator_items,
                    using=BWDatabaseRouter.get_write_database_name()
                )
                print("processed.")

            if len(creatable_poverty_indices) > 0:
                print("processing {} {} items.".format(len(creatable_poverty_indices), PGPovertyIndex.__name__))
                PGPovertyIndex.objects.using(
                    BWDatabaseRouter.get_write_database_name()
                ).bulk_create(creatable_poverty_indices)
                print("processed.")

            if len(updatable_business_items) > 0:
                print("processing {} {} items.".format(
                    len(updatable_business_items), EligibleBusinessGrantee.__name__))
                EligibleBusinessGrantee.objects.bulk_update(
                    objs=updatable_business_items,
                    using=BWDatabaseRouter.get_write_database_name()
                )
                print("processed.")

            if len(updatable_apprenticeship_items) > 0:
                print("processing {} {} items.".format(
                    len(updatable_apprenticeship_items), EligibleApprenticeshipGrantee.__name__))
                EligibleApprenticeshipGrantee.objects.bulk_update(
                    objs=updatable_apprenticeship_items,
                    using=BWDatabaseRouter.get_write_database_name()
                )
                print("processed.")

            if len(updatable_drop_out_items) > 0:
                print("processing {} {} items.".format(
                    len(updatable_drop_out_items), EligibleEducationDropOutGrantee.__name__))
                EligibleEducationDropOutGrantee.objects.bulk_update(
                    objs=updatable_drop_out_items,
                    using=BWDatabaseRouter.get_write_database_name()
                )
                print("processed.")

            if len(updatable_early_marriage_items) > 0:
                print("processing {} {} items.".format(
                    len(updatable_early_marriage_items), EligibleEducationEarlyMarriageGrantee.__name__))
                EligibleEducationEarlyMarriageGrantee.objects.bulk_update(
                    objs=updatable_early_marriage_items,
                    using=BWDatabaseRouter.get_write_database_name()
                )
                print("processed.")

            offset += 1000
            limit += 1000
            print("Max processed ID: {0}".format(max_processed_id))
