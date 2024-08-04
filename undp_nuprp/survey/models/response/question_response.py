from django.db import models, transaction

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Tareq'


class QuestionResponse(OrganizationDomainEntity):
    section_response = models.ForeignKey('survey.SectionResponse', on_delete=models.CASCADE)
    question = models.ForeignKey('survey.Question', on_delete=models.CASCADE)
    answer = models.ForeignKey('survey.Answer', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1024, blank=True, db_index=True)
    answer_text = models.CharField(max_length=2048, blank=True, db_index=True)
    index = models.IntegerField(default=0)

    @classmethod
    def get_serializer(cls):
        ode_serializer = OrganizationDomainEntity.get_serializer()

        class QuestionResponseSerializer(ode_serializer):
            class Meta:
                model = cls
                fields = 'section_response', 'question', 'answer', 'question_text', 'answer_text', 'index'

        return QuestionResponseSerializer

    @classmethod
    def update_master_version(cls, deletable_qr_ids):
        '''
        Purpose: Whenever a QR object is deleted it's child objects need to reassign. For this, we consider the
        immediate next QR objects as new parent and assign it to its immediate next QR. This process continue for all
        available QR objects of given parent QR(master object)
        :param deletable_qr_ids: child survey response ID
        :return:
        '''

        with transaction.atomic():
            for deletable_qr_id in deletable_qr_ids:
                child_qrs = cls.objects_include_versions.filter(master_version_id=deletable_qr_id).order_by(
                    'pk')

                _updated_master_version = None
                for child_qr in child_qrs:
                    child_qr.master_version = _updated_master_version
                    _updated_master_version = child_qr
                    child_qr.save()

            cls.objects.filter(id__in=deletable_qr_ids).delete()

    class Meta:
        app_label = 'survey'
