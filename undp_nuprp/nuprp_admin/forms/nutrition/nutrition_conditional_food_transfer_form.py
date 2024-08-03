import calendar
from datetime import date

from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.nutrition.nutrition_conditional_food_transfer import NutritionConditionalFoodTransfer


class NutritionConditionalFoodTransferForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(NutritionConditionalFoodTransferForm, self).__init__(data=data, files=files, instance=instance,
                                                     prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['month'] = forms.ChoiceField(
            choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
            initial=date.today().month if not instance else instance.month,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ),
            required=False
        )

        self.fields['year'] = forms.ChoiceField(
            required=False,
            choices=[(y, str(y)) for y in range(2000, 2100)],
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ),
            initial=date.today().year if not instance else instance.year,
        )

        self.fields['no_of_pregnant_women_by_age_lt_20'].required = False
        self.fields['no_of_pregnant_women_by_age_20_25'].required = False
        self.fields['no_of_pregnant_women_by_age_26_30'].required = False
        self.fields['no_of_pregnant_women_by_age_31_35'].required = False
        self.fields['no_of_pregnant_women_by_age_36_40'].required = False
        self.fields['no_of_pregnant_women_by_age_41_45'].required = False
        self.fields['no_of_pregnant_women_by_age_46_50'].required = False
        self.fields['no_of_pregnant_women_by_age_gt_50'].required = False
        self.fields['no_of_lactating_mothers_by_age_lt_20'].required = False
        self.fields['no_of_lactating_mothers_by_age_20_25'].required = False
        self.fields['no_of_lactating_mothers_by_age_26_30'].required = False
        self.fields['no_of_lactating_mothers_by_age_31_35'].required = False
        self.fields['no_of_lactating_mothers_by_age_36_40'].required = False
        self.fields['no_of_lactating_mothers_by_age_41_45'].required = False
        self.fields['no_of_lactating_mothers_by_age_46_50'].required = False
        self.fields['no_of_lactating_mothers_by_age_gt_50'].required = False
        self.fields['no_of_child_0_6_months_by_male'].required = False
        self.fields['no_of_child_0_6_months_by_female'].required = False
        self.fields['no_of_child_0_6_months_by_transgender'].required = False
        self.fields['no_of_child_7_24_months_by_male'].required = False
        self.fields['no_of_child_7_24_months_by_female'].required = False
        self.fields['no_of_child_7_24_months_by_transgender'].required = False

    class Meta(GenericFormMixin.Meta):
        model = NutritionConditionalFoodTransfer
        fields = (
            'city', 'month', 'year',
            'no_of_pregnant_women_by_age_lt_20',
            'no_of_pregnant_women_by_age_20_25',
            'no_of_pregnant_women_by_age_26_30',
            'no_of_pregnant_women_by_age_31_35',
            'no_of_pregnant_women_by_age_36_40',
            'no_of_pregnant_women_by_age_41_45',
            'no_of_pregnant_women_by_age_46_50',
            'no_of_pregnant_women_by_age_gt_50',
            'no_of_lactating_mothers_by_age_lt_20',
            'no_of_lactating_mothers_by_age_20_25',
            'no_of_lactating_mothers_by_age_26_30',
            'no_of_lactating_mothers_by_age_31_35',
            'no_of_lactating_mothers_by_age_36_40',
            'no_of_lactating_mothers_by_age_41_45',
            'no_of_lactating_mothers_by_age_46_50',
            'no_of_lactating_mothers_by_age_gt_50',
            'no_of_child_0_6_months_by_male',
            'no_of_child_0_6_months_by_female',
            'no_of_child_0_6_months_by_transgender',
            'no_of_child_7_24_months_by_male',
            'no_of_child_7_24_months_by_female',
            'no_of_child_7_24_months_by_transgender',
        )
        labels = {
            'no_of_pregnant_women_by_age_lt_20': 'No of pregnant women by age < 20',
            'no_of_pregnant_women_by_age_20_25': 'No of pregnant women by age 20-25',
            'no_of_pregnant_women_by_age_26_30': 'No of pregnant women by age 26-30',
            'no_of_pregnant_women_by_age_31_35': 'No of pregnant women by age 31-35',
            'no_of_pregnant_women_by_age_36_40': 'No of pregnant women by age 36-40',
            'no_of_pregnant_women_by_age_41_45': 'No of pregnant women by age 41-45',
            'no_of_pregnant_women_by_age_46_50': 'No of pregnant women by age 46-50',
            'no_of_pregnant_women_by_age_gt_50': 'No of pregnant women by age > 50',
            'no_of_lactating_mothers_by_age_lt_20': 'No of lactating mothers by age < 20',
            'no_of_lactating_mothers_by_age_20_25': 'No of lactating mothers by age 20-25',
            'no_of_lactating_mothers_by_age_26_30': 'No of lactating mothers by age 26-30',
            'no_of_lactating_mothers_by_age_31_35': 'No of lactating mothers by age 31-35',
            'no_of_lactating_mothers_by_age_36_40': 'No of lactating mothers by age 36-40',
            'no_of_lactating_mothers_by_age_41_45': 'No of lactating mothers by age 41-45',
            'no_of_lactating_mothers_by_age_46_50': 'No of lactating mothers by age 46-50',
            'no_of_lactating_mothers_by_age_gt_50': 'No of lactating mothers by age > 50',
            'no_of_child_0_6_months_by_male': 'No of child 0-6 months Male',
            'no_of_child_0_6_months_by_female': 'No of child 0-6 months Female',
            'no_of_child_0_6_months_by_transgender': 'No of child 0-6 months Transgender',
            'no_of_child_7_24_months_by_male': 'No of child 7-24 months Male',
            'no_of_child_7_24_months_by_female': 'No of child 7-24 months Female',
            'no_of_child_7_24_months_by_transgender': 'No of child 7-24 months Transgender'
        }

    @classmethod
    def field_groups(cls):
        _group = super(NutritionConditionalFoodTransferForm, cls).field_groups()
        _group['No of pregnant women by age group'] = \
            ['no_of_pregnant_women_by_age_lt_20',
             'no_of_pregnant_women_by_age_20_25',
             'no_of_pregnant_women_by_age_26_30',
             'no_of_pregnant_women_by_age_31_35',
             'no_of_pregnant_women_by_age_36_40',
             'no_of_pregnant_women_by_age_41_45',
             'no_of_pregnant_women_by_age_46_50',
             'no_of_pregnant_women_by_age_gt_50']

        _group['No of lactating mothers by age group'] = \
            ['no_of_lactating_mothers_by_age_lt_20',
             'no_of_lactating_mothers_by_age_20_25',
             'no_of_lactating_mothers_by_age_26_30',
             'no_of_lactating_mothers_by_age_31_35',
             'no_of_lactating_mothers_by_age_36_40',
             'no_of_lactating_mothers_by_age_41_45',
             'no_of_lactating_mothers_by_age_46_50',
             'no_of_lactating_mothers_by_age_gt_50']

        _group['No of child 0-6 months by sex'] = \
            ['no_of_child_0_6_months_by_male',
             'no_of_child_0_6_months_by_female',
             'no_of_child_0_6_months_by_transgender']

        _group['No of child 7-24 months by sex'] = \
            ['no_of_child_7_24_months_by_male',
             'no_of_child_7_24_months_by_female',
             'no_of_child_7_24_months_by_transgender']

        return _group
