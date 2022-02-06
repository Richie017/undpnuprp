from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.clients.client_supporter import ClientSupporter
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.imagefileobject import ImageFileObject

__author__ = 'ruddra'

_CHOICES_HF = (
    ('H', 'Husband'),
    ('F', 'Father'),
)

_CHOICES_MF = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('H', 'Hijra'),
)

_CHOICES_SM = (
    ('S', 'Single'),
    ('M', 'Married')
)


class ClientMeta(OrganizationDomainEntity):
    gender = models.CharField(max_length=2, choices=_CHOICES_MF, null=True, default='M')
    guardian_name = models.CharField(max_length=255, verbose_name="Husband or Father's Name", null=True, default=None)
    guardian_choice_type = models.CharField(max_length=2, choices=_CHOICES_HF, verbose_name='Husband or Father',
                                            null=True, default='H')
    selling_area = models.CharField(max_length=255, null=True, default=None,
                                    verbose_name='Selling area or selling village')
    date_of_birth = models.DateTimeField(default=None, null=True)
    national_id = models.CharField(max_length=200, null=True)
    nid_image = models.ForeignKey(ImageFileObject, null=True, default=None)
    p_photo = models.ForeignKey(ImageFileObject, null=True, default=None, related_name="personal_photo")
    comments = models.CharField(max_length=500, null=True, blank=True, default='')
    start_of_company_relationship = models.CharField(max_length=200, default='')
    marital_status = models.CharField(max_length=2, choices=_CHOICES_SM, null=True, default='S')
    number_of_children = models.IntegerField(default=0)
    age = models.IntegerField(default=0)
    vehicle_details = models.CharField(max_length=200, null=True)
    working_experience = models.CharField(max_length=200, null=True)
    participation_details = models.CharField(max_length=200, null=True)
    is_disabled = models.BooleanField(default=False)
    supporter_one = models.ForeignKey(ClientSupporter, null=True, default=None, related_name="supporter_one",
                                      on_delete=models.SET_NULL)
    supporter_two = models.ForeignKey(ClientSupporter, null=True, default=None, related_name="supporter_two",
                                      on_delete=models.SET_NULL)
    supporter_three = models.ForeignKey(ClientSupporter, null=True, default=None, related_name="supporter_three",
                                        on_delete=models.SET_NULL)

    def __str__(self):
        return mark_safe("<b>Date of Birth:</b> " + self.date_of_birth.strftime(
            "%d/%m/%Y") if self.date_of_birth is not None else '' + '<br/>'
                                                               + "<b>ID No:</b> " + self.national_id if self.national_id is not None else '' + '<br/>'
                                                                                                                                          + "<b>Marital Status:</b> " + self.marital_status if self.marital_status is not None else '' + '<br/>')

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            national_id = ImageFileObject.get_serializer()(required=False)
            p_photo = ImageFileObject.get_serializer()(required=False)

            class Meta(ss.Meta):
                model = cls
                fields = (
                    'id', 'code', 'selling_area', 'date_of_birth', 'national_id',
                    'nid_image', 'p_photo', 'comments', 'start_of_company_relationship')

        return Serializer
