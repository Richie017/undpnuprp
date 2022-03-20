"""
    Created by tareq on 9/22/19
"""
from collections import OrderedDict

from django.db import models
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.enums.capacity_building_organization_enum import CapacityBuildingOrganizationEnum
from undp_nuprp.nuprp_admin.enums.capacity_building_type_enum import CapacityBuildingTypeEnum

__author__ = "Tareq"


@decorate(is_object_context, route(route='capacity-building', group='Capacity Building', module=ModuleEnum.Analysis,
                                   display_name='Capacity Building', group_order=7, item_order=3)
          )
class CapacityBuilding(OrganizationDomainEntity):
    title = models.CharField(max_length=255, blank=True)
    output = models.CharField(max_length=255, blank=True)
    type_of_capacity_building = models.SmallIntegerField(null=True)
    specify_if_other_type_of_cb = models.TextField(blank=True)

    city = models.ForeignKey('core.Geography', null=True)

    batched_planned = models.IntegerField(default=0)
    batched_held = models.IntegerField(default=0)
    cumulative_male = models.IntegerField(default=0)
    cumulative_female = models.IntegerField(default=0)
    cumulative_disabled = models.IntegerField(default=0)

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    duration = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    number_of_male_cluster_leader = models.IntegerField(default=0)
    number_of_female_cluster_leader = models.IntegerField(default=0)
    number_of_disabled_cluster_leader = models.IntegerField(default=0)
    number_of_male_cluster_member = models.IntegerField(default=0)
    number_of_female_cluster_member = models.IntegerField(default=0)
    number_of_disabled_cluster_member = models.IntegerField(default=0)
    number_of_male_elected = models.IntegerField(default=0)
    number_of_female_elected = models.IntegerField(default=0)
    number_of_disabled_elected = models.IntegerField(default=0)
    number_of_male_town_staff = models.IntegerField(default=0)
    number_of_female_town_staff = models.IntegerField(default=0)
    number_of_disabled_town_staff = models.IntegerField(default=0)
    number_of_male_other = models.IntegerField(default=0)
    number_of_female_other = models.IntegerField(default=0)
    number_of_disabled_other = models.IntegerField(default=0)
    specify_if_other = models.TextField(blank=True)

    total_male = models.IntegerField(default=0)
    total_female = models.IntegerField(default=0)
    total_disabled = models.IntegerField(default=0)
    total_number_of_people = models.IntegerField(default=0)
    total_training_person_days = models.IntegerField(default=0)

    total_cost = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    organized_by = models.SmallIntegerField(null=True)
    specify_if_other_organizer = models.TextField(blank=True)

    venue = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    
    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit,
            ViewActionEnum.AdvancedExport, ViewActionEnum.Delete
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        return button
    
    def save(self, *args, organization=None, **kwargs):
        
        self.total_male = self.number_of_male_cluster_leader + self.number_of_male_cluster_member + \
                          self.number_of_male_elected + self.number_of_male_town_staff + self.number_of_male_other
        self.total_female = self.number_of_female_cluster_leader + self.number_of_female_cluster_member + \
                            self.number_of_female_elected + self.number_of_female_town_staff + \
                            self.number_of_female_other
        self.total_disabled = self.number_of_disabled_cluster_leader + self.number_of_disabled_cluster_member + \
                              self.number_of_disabled_elected + self.number_of_disabled_town_staff + \
                              self.number_of_disabled_other
        self.total_number_of_people = self.total_male + self.total_female
        self.total_training_person_days = self.total_number_of_people * self.duration

        super(CapacityBuilding, self).save(*args, organization=organization, **kwargs)

        

    @property
    def render_detail_title(self):
        return mark_safe(str(self.title))

    @property
    def render_type_of_capacity_building(self):
        return CapacityBuildingTypeEnum.get_name_from_value(self.type_of_capacity_building)

    @property
    def render_organized_by(self):
        return CapacityBuildingOrganizationEnum.get_name_from_value(self.organized_by)

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'title', 'city', 'render_type_of_capacity_building', 'start_date', 'end_date', 'total_cost',
            'render_organized_by', 'created_by', 'last_updated_by', 'last_updated'
        ]

    @classmethod
    def export_file_columns(cls):
        return [
            'code', 'title', 'city', 'output', 'render_type_of_capacity_building:Type of Capacity Building Activity',

            'batched_planned:No. of total Courses/batches Planned > Cumulative Progress',
            'batched_held:No. of total Courses/batches Held > Cumulative Progress',
            'render_cumulative_male:Male > Cumulative Progress',
            'render_cumulative_female:Female > Cumulative Progress',
            'render_cumulative_disabled:Person with disabilities > Cumulative Progress',
            'render_cumulative_progress_total:Total > Cumulative Progress',

            'start_date:Start date > Participants and Cost in the Reporting Month',
            'end_date:End date > Participants and Cost in the Reporting Month',
            'duration:Duration > Participants and Cost in the Reporting Month',

            'render_number_of_male_cluster_leader:No of PG/CDC/Cluster Leaders (male) > Participants and Cost in the Reporting Month',
            'render_number_of_female_cluster_leader:No of PG/CDC/Cluster Leaders (female) > Participants and Cost in the Reporting Month',
            'render_number_of_disabled_cluster_leader:No of PG/CDC/Cluster Leaders (person with disabilities) > Participants and Cost in the Reporting Month',

            'render_number_of_male_cluster_member:No of PG/CDC/Cluster members (male) > Participants and Cost in the Reporting Month',
            'render_number_of_female_cluster_member:No of PG/CDC/Cluster members (female) > Participants and Cost in the Reporting Month',
            'render_number_of_disabled_cluster_member:No of PG/CDC/Cluster members (person with disabilities) > Participants and Cost in the Reporting Month',

            'render_number_of_male_elected:No of Local Elected Person (male) > Participants and Cost in the Reporting Month',
            'render_number_of_female_elected:No of Local Elected Person (female) > Participants and Cost in the Reporting Month',
            'render_number_of_disabled_elected:No of Local Elected Person (person with disabilities) > Participants and Cost in the Reporting Month',

            'render_number_of_male_town_staff:No of Town Staff (male) > Participants and Cost in the Reporting Month',
            'render_number_of_female_town_staff:No of Town Staff (female) > Participants and Cost in the Reporting Month',
            'render_number_of_disabled_town_staff:No of Town Staff (person with disabilities) > Participants and Cost in the Reporting Month',

            'render_number_of_male_other:Other (male) > Participants and Cost in the Reporting Month',
            'render_number_of_female_other:Other (female) > Participants and Cost in the Reporting Month',
            'render_number_of_disabled_other:Other (person with disabilities) > Participants and Cost in the Reporting Month',

            'specify_if_other:Specify if other > Participants and Cost in the Reporting Month',
            'render_total_male:Total male > Participants and Cost in the Reporting Month',
            'render_total_female:Total female > Participants and Cost in the Reporting Month',
            'render_total_disabled:Total person with disabilities > Participants and Cost in the Reporting Month',

            'render_total_number_of_people:Total (male + female + person with disabilities) > Participants and Cost in the Reporting Month',
            'render_total_training_person_days:Total training person Days > Participants and Cost in the Reporting Month',
            'render_total_cost:Total Cost (Tk.) > Participants and Cost in the Reporting Month',
            'render_organized_by:Organized by > Participants and Cost in the Reporting Month',
            'venue:Venue > Participants and Cost in the Reporting Month',

            'remarks:Remarks > Remarks',
            'created_by', 'last_updated_by',
        ]

    @property
    def render_total_number_of_people(self):
        return self.total_number_of_people if self.total_number_of_people else str(0)

    @property
    def render_total_training_person_days(self):
        return self.total_training_person_days if self.total_training_person_days else str(0)

    @property
    def render_total_cost(self):
        return self.total_cost if self.total_cost else str(0)

    @property
    def render_total_male(self):
        return self.total_male if self.total_male else str(0)

    @property
    def render_total_female(self):
        return self.total_female if self.total_female else str(0)

    @property
    def render_total_disabled(self):
        return self.total_disabled if self.total_disabled else str(0)

    @property
    def render_number_of_male_other(self):
        return self.number_of_male_other if self.number_of_male_other else str(0)

    @property
    def render_number_of_female_other(self):
        return self.number_of_female_other if self.number_of_female_other else str(0)

    @property
    def render_number_of_disabled_other(self):
        return self.number_of_disabled_other if self.number_of_disabled_other else str(0)

    @property
    def render_number_of_male_town_staff(self):
        return self.number_of_male_town_staff if self.number_of_male_town_staff else str(0)

    @property
    def render_number_of_female_town_staff(self):
        return self.number_of_female_town_staff if self.number_of_female_town_staff else str(0)

    @property
    def render_number_of_disabled_town_staff(self):
        return self.number_of_disabled_town_staff if self.number_of_disabled_town_staff else str(0)

    @property
    def render_number_of_male_elected(self):
        return self.number_of_male_elected if self.number_of_male_elected else str(0)

    @property
    def render_number_of_female_elected(self):
        return self.number_of_female_elected if self.number_of_female_elected else str(0)

    @property
    def render_number_of_disabled_elected(self):
        return self.number_of_disabled_elected if self.number_of_disabled_elected else str(0)

    @property
    def render_number_of_male_cluster_member(self):
        return self.number_of_male_cluster_member if self.number_of_male_cluster_member else str(0)

    @property
    def render_number_of_female_cluster_member(self):
        return self.number_of_female_cluster_member if self.number_of_female_cluster_member else str(0)

    @property
    def render_number_of_disabled_cluster_member(self):
        return self.number_of_disabled_cluster_member if self.number_of_disabled_cluster_member else str(0)

    @property
    def render_number_of_disabled_cluster_leader(self):
        return self.number_of_disabled_cluster_leader if self.number_of_disabled_cluster_leader else str(0)

    @property
    def render_number_of_male_cluster_leader(self):
        return self.number_of_male_cluster_leader if self.number_of_male_cluster_leader else str(0)

    @property
    def render_number_of_female_cluster_leader(self):
        return self.number_of_female_cluster_leader if self.number_of_female_cluster_leader else str(0)

    @property
    def render_cumulative_progress_total(self):
        _total = self.cumulative_female + self.cumulative_male
        return _total if _total else str(0)

    @property
    def render_cumulative_disabled(self):
        return self.cumulative_disabled if self.cumulative_disabled else str(0)

    @property
    def render_cumulative_female(self):
        return self.cumulative_female if self.cumulative_female else str(0)

    @property
    def render_cumulative_male(self):
        return self.cumulative_male if self.cumulative_male else str(0)

    @property
    def details_config(self):
        d = OrderedDict()
        d['detail_title'] = self.render_detail_title
        d['Output'] = self.output
        d['Type of Capacity Building Activity'] = self.render_type_of_capacity_building
        d['Title'] = self.title
        d['City'] = self.city

        d['Cumulative Progress'] = OrderedDict()
        d['Cumulative Progress']['No. of total Courses/batches Planned'] = self.batched_planned
        d['Cumulative Progress']['No. of total Courses/batches Held'] = self.batched_held
        d['Cumulative Progress']['Male'] = self.render_cumulative_male
        d['Cumulative Progress']['Female'] = self.render_cumulative_female
        d['Cumulative Progress']['Person with disabilities'] = self.render_cumulative_disabled
        d['Cumulative Progress']['Total'] = self.render_cumulative_progress_total

        d['Participants and Cost in the Reporting Month'] = OrderedDict()
        d['Participants and Cost in the Reporting Month']['start_date'] = self.start_date
        d['Participants and Cost in the Reporting Month']['end_date'] = self.end_date
        d['Participants and Cost in the Reporting Month']['duration'] = self.duration
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster Leaders (male)'] = self.number_of_male_cluster_leader
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster Leaders (female)'] = self.number_of_female_cluster_leader
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster Leaders (person with disabilities)'] = self.number_of_disabled_cluster_leader
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster members (male)'] = self.number_of_male_cluster_member
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster members (female)'] = self.number_of_female_cluster_member
        d['Participants and Cost in the Reporting Month'][
            'No of PG/CDC/Cluster members (person with disabilities)'] = self.number_of_disabled_cluster_member
        d['Participants and Cost in the Reporting Month'][
            'No of Local Elected Person (male)'] = self.number_of_male_elected
        d['Participants and Cost in the Reporting Month'][
            'No of Local Elected Person (female)'] = self.number_of_female_elected
        d['Participants and Cost in the Reporting Month'][
            'No of Local Elected Person (person with disabilities)'] = self.number_of_disabled_elected
        d['Participants and Cost in the Reporting Month']['No of Town Staff (male)'] = self.number_of_male_town_staff
        d['Participants and Cost in the Reporting Month'][
            'No of Town Staff (female)'] = self.number_of_female_town_staff
        d['Participants and Cost in the Reporting Month'][
            'No of Town Staff (person with disabilities)'] = self.number_of_disabled_town_staff
        d['Participants and Cost in the Reporting Month']['Other (male)'] = self.number_of_male_other
        d['Participants and Cost in the Reporting Month']['Other (female)'] = self.number_of_female_other
        d['Participants and Cost in the Reporting Month']['Other (person with disabilities)'] = self.number_of_disabled_other
        d['Participants and Cost in the Reporting Month']['Specify if other'] = self.specify_if_other
        d['Participants and Cost in the Reporting Month']['Total male'] = self.total_male
        d['Participants and Cost in the Reporting Month']['Total female'] = self.total_female
        d['Participants and Cost in the Reporting Month']['Total person with disabilities'] = self.total_disabled
        d['Participants and Cost in the Reporting Month']['Total (male + female + person with disabilities)'] = self.total_number_of_people
        d['Participants and Cost in the Reporting Month'][
            'Total training person Days'] = self.total_training_person_days
        d['Participants and Cost in the Reporting Month']['Total Cost (Tk.)'] = self.total_cost
        d['Participants and Cost in the Reporting Month']['Organized by'] = self.render_organized_by
        d['Participants and Cost in the Reporting Month']['venue'] = self.venue
        d['Remarks'] = OrderedDict()
        d['Remarks']['Remarks'] = self.remarks

        return d
