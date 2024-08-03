from django.core.management import BaseCommand
from django.db.models import Q

from blackwidow.core.models import Geography
from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationChildMarriageGrantee, \
    SEFEducationDropoutGrantee, SEFNutritionGrantee


class Command(BaseCommand):
    def handle(self, *args, **options):

        model_list = [
            SEFBusinessGrantee,
            SEFApprenticeshipGrantee,
            SEFEducationChildMarriageGrantee,
            SEFEducationDropoutGrantee,
            SEFNutritionGrantee
        ]
        for _m in model_list:
            print('started ' + str(_m))
            updateable_list = list()
            queryset = _m.objects.all()
            for item in queryset:
                city = item.pg_member.assigned_to.parent.address.geography.parent if item.pg_member else None
                ward_no = item.pg_member_assigned_code[3:5]
                if city and ward_no:
                    ward_ = Geography.objects.filter(
                        Q(name__iexact=ward_no) | Q(name__iexact=ward_no.zfill(2)),
                        level__name='Ward',
                        parent=city
                    ).first()
                    if ward_:
                        item.ward = ward_.name
                        updateable_list.append(item)
            _m.objects.bulk_update(updateable_list, batch_size=2000)
            print("completed " + str(_m))
