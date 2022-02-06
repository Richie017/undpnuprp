from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.educational_qualification import EducationalQualification

__author__ = 'ruddra'


class EQualificationForm(GenericFormMixin):

    class Meta(GenericFormMixin.Meta):
        model = EducationalQualification
        fields = ['degree', 'year', 'institute', 'board', 'result']
