from blackwidow.engine.extensions import Clock
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count, Max, Min
from blackwidow.core.models.contracts.base import DomainEntity
from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationChildMarriageGrantee, \
    SEFEducationDropoutGrantee, SEFNutritionGrantee

__author__ = 'Kaikobud'


class SEFGranteesInfoCache(DomainEntity):
    year = models.IntegerField(default=1970)
    month = models.IntegerField(default=1)
    day = models.IntegerField(default=1)
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL, related_name='+')
    ward = models.CharField(null=True, blank=True, max_length=20)
    no_of_business_grantee = models.IntegerField(default=0)
    no_of_apprenticeship_grantee = models.IntegerField(default=0)
    no_of_education_dropout_grantee = models.IntegerField(default=0)
    no_education_early_marriage_grantee = models.IntegerField(default=0)
    no_of_nutrition_grantees = models.IntegerField(default=0)

    class Meta:
        app_label = 'reports'

    @classmethod
    def generate_sef_grantees_info_cache(cls):
        model_list = [(SEFBusinessGrantee, 'no_of_business_grantee'),
                      (SEFApprenticeshipGrantee, 'no_of_apprenticeship_grantee'),
                      (SEFEducationChildMarriageGrantee, 'no_education_early_marriage_grantee'),
                      (SEFEducationDropoutGrantee, 'no_of_education_dropout_grantee'),
                      (SEFNutritionGrantee, 'no_of_nutrition_grantees')]

        # get last object creation date to identify starting date for generating latest cache
        # cache is always generated data until previous day based on the task execution date
        last_created_date = SEFGranteesInfoCache.objects.aggregate(Max('date_created'))['date_created__max']
        if last_created_date is None:
            from_date = SEFBusinessGrantee.objects.aggregate(Min('date_created'))['date_created__min']
            for model in model_list[1:]:
                first_created_date = model[0].objects.aggregate(Min('date_created'))['date_created__min']
                if first_created_date and first_created_date < from_date:
                    from_date = first_created_date
            from_date = datetime.fromtimestamp(from_date / 1000)
        else:
            from_date = datetime.fromtimestamp(last_created_date / 1000)
        to_date = datetime.now() - timedelta(days=1)

        while from_date.date() <= to_date.date():
            creatable_data = []
            data_dict = dict()
            date = from_date.date()
            _from_time = from_date.replace(hour=0, minute=0, second=0).timestamp() * 1000
            _to_time = from_date.replace(hour=23, minute=59, second=59).timestamp() * 1000
            for item in model_list:
                queryset = item[0].objects.filter(date_created__gte=_from_time, date_created__lte=_to_time,is_deleted=False,is_version=False,is_active=True). \
                    values('pg_member__assigned_to__parent__address__geography__parent_id', 'ward').annotate(Count('id'))
                for query in queryset:
                    city_id = query['pg_member__assigned_to__parent__address__geography__parent_id']
                    ward = query['ward']
                    if city_id not in data_dict.keys():
                        data_dict[(city_id, ward)] = {
                            'no_of_business_grantee': 0,
                            'no_of_apprenticeship_grantee': 0,
                            'no_of_education_dropout_grantee': 0,
                            'no_education_early_marriage_grantee': 0,
                            'no_of_nutrition_grantees': 0,
                        }

                    data_dict[(city_id, ward)][item[1]] = query['id__count']

            timestamp = Clock.timestamp()
            for city_ward, values in data_dict.items():
                city, ward = city_ward
                record = SEFGranteesInfoCache(year=date.year, month=date.month, day=date.day, city_id=city, ward=ward)
                record.no_of_business_grantee = values['no_of_business_grantee']
                record.no_of_apprenticeship_grantee = values['no_of_apprenticeship_grantee']
                record.no_of_education_dropout_grantee = values['no_of_education_dropout_grantee']
                record.no_education_early_marriage_grantee = values['no_education_early_marriage_grantee']
                record.no_of_nutrition_grantees = values['no_of_nutrition_grantees']
                record.date_created = timestamp
                record.last_updated = timestamp
                creatable_data.append(record)
                timestamp += 1

            SEFGranteesInfoCache.objects.bulk_create(creatable_data)
            from_date += timedelta(days=1)
