from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Sohel'


class Report(OrganizationDomainEntity):

    class Meta:
        app_label = 'reports'

    @classmethod
    def manage_action_config(cls):
        return []

    @classmethod
    def get_filtered_data(cls, _request, _model, _queryset=None):
        _user = _request.c_user.to_business_user()
        if _queryset is None:
            _queryset = _model.objects.all()
        _queryset = _model.get_queryset(queryset=_queryset, user=_user, profile_filter=not _user.is_super)
        _queryset = _user.filter_model(request=_request, queryset=_queryset)
        return _model.apply_search_filter(request=_request.GET, queryset=_queryset)
