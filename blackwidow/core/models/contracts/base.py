import copy
import datetime
import random
import string
import uuid
from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from threading import Thread

from crequest.middleware import CrequestMiddleware
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey, OneToOneField

from blackwidow.core.mixins.modelmixin.active_inactive_model_mixin import ActiveInactiveModelMixin
from blackwidow.core.mixins.modelmixin.approval_process_restore_model_mixin import ApprovalRestoreModelMixin
from blackwidow.core.mixins.modelmixin.assignment_tracked_model_mixin import AssignmentTrackedModelMixin
from blackwidow.core.mixins.modelmixin.editable_model_mixin import EditableModelMixin
from blackwidow.core.mixins.modelmixin.exportable_model_mixin import ExportableModelMixin
from blackwidow.core.mixins.modelmixin.prefetch_related_model_mixin import PrefetchRelatedModelMixin
from blackwidow.core.mixins.modelmixin.restorable_model_mixin import RestorableModelMixin
from blackwidow.core.mixins.modelmixin.step_back_model_mixin import StepBackExecuteModelMixin
from blackwidow.core.mixins.modelmixin.versioning_model_mixin import VersioningModelMixin
from blackwidow.engine.mixins.modelmixin.queryset_cache_mixin import QuerysetCacheMixin

get_model = apps.get_model
from django.db.models.manager import Manager
from django.db.models.signals import post_save
from django.http.request import HttpRequest
from rest_framework import serializers

from blackwidow.core.managers.modelmanager import DomainEntityModelManager, DomainEntityIncludeInactiveModelManager, \
    DomainEntityIncludeDeletedModelManager, DomainEntityIncludeAllModelManager, DomainEntityVersionModelManager, \
    DomainEntityIncludeVersionsModelManager
from blackwidow.core.mixins.modelmixin.auditable_model_mixin import AuditableModelMixin
from blackwidow.core.mixins.modelmixin.child_container_model_mixin import ChildContainerModelMixin
from blackwidow.core.mixins.modelmixin.coded_model_mixin import CodedModelMixin
from blackwidow.core.mixins.modelmixin.convertible_model_mixin import MutableModelMixin, ApprovableModelMixin, \
    RejectableModelMixin
from blackwidow.core.mixins.modelmixin.details_view_model_mixin import DetailsViewModelMixin
from blackwidow.core.mixins.modelmixin.list_view_model_mixin import ListViewModelMixin
from blackwidow.core.mixins.modelmixin.mapped_model_mixin import MappedModelMixin
from blackwidow.core.mixins.modelmixin.proxy_model_mixin import ProxyModelMixin
from blackwidow.core.mixins.modelmixin.restricted_model_mixin import RestrictedModelMixin
from blackwidow.core.mixins.modelmixin.routed_model_mixin import RoutedModelMixin
from blackwidow.core.mixins.modelmixin.searchable_model_mixin import SearchableModelMixin
from blackwidow.core.mixins.modelmixin.serializable_model_mixin import SerializableModelMixin
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.exceptions.exceptions import EntityNotDeletableException


class CreationFlag(Enum):
    Imported = 'Imported'
    Created = 'Created'


class RequestSource(Enum):
    MobileDevice = 'Mobile Device'
    WebBrowser = 'Web Browser'


class DomainEntity(ListViewModelMixin, DetailsViewModelMixin, SerializableModelMixin, RoutedModelMixin,
                   AuditableModelMixin, EditableModelMixin, AssignmentTrackedModelMixin, RestorableModelMixin,
                   ProxyModelMixin, MappedModelMixin, CodedModelMixin, ChildContainerModelMixin, SearchableModelMixin,
                   RestrictedModelMixin, MutableModelMixin, ApprovableModelMixin, RejectableModelMixin,
                   ActiveInactiveModelMixin, StepBackExecuteModelMixin, ApprovalRestoreModelMixin, QuerysetCacheMixin,
                   ExportableModelMixin, PrefetchRelatedModelMixin, VersioningModelMixin, models.Model):
    # private
    _decorators = {}
    # default properties
    tsync_id = models.CharField(max_length=55, null=True, blank=True, db_index=True)
    date_created = models.BigIntegerField(editable=False, default=0)
    last_updated = models.BigIntegerField(editable=False, default=0)
    is_active = models.BooleanField(default=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)
    is_locked = models.BooleanField(default=False, editable=False)
    created_by = models.ForeignKey('core.ConsoleUser', related_name='+', null=True, on_delete=models.SET_NULL)
    last_updated_by = models.ForeignKey('core.ConsoleUser', related_name='+', null=True, on_delete=models.SET_NULL)
    creation_flag = models.CharField(max_length=200, default=CreationFlag.Created.value)
    type = models.CharField(max_length=200, default='', db_index=True)
    code = models.CharField(default='', max_length=200)
    deleted_level = models.SmallIntegerField(default=0)
    entity_meta = models.ForeignKey('core.DomainEntityMeta', null=True, on_delete=models.SET_NULL)
    master_version = models.ForeignKey('self', related_name='version_master', null=True)
    is_version = models.BooleanField(default=False, editable=False)

    ## Model Managers.
    '''
        DomainEntity.objects will refer Active, Undeleted members of the model
        DomainEntity.undeleted_objects will refer all Undeleted members of the model
        DomainEntity.active_objects will refer all Active members of the model
        DomainEntity.all_objects will refer all members of the model including deleted and inactive members
    '''
    objects = DomainEntityModelManager()
    undeleted_objects = DomainEntityIncludeInactiveModelManager()
    active_objects = DomainEntityIncludeDeletedModelManager()
    all_objects = DomainEntityIncludeAllModelManager()
    version_objects = DomainEntityVersionModelManager()
    objects_include_versions = DomainEntityIncludeVersionsModelManager()

    def final_approval_action(self, action, *args, **kwargs):  ###action can be either APPROVED or REJECTED
        pass

    @property
    def render_date_created(self, **kwargs):
        return Clock.get_user_local_time(self.date_created).strftime('%d/%m/%Y - %I:%M %p')

    @classmethod
    def post_processing_import_completed(cls, items=None, user=None, organization=None, **kwargs):
        pass

    @classmethod
    def get_queryset(cls, queryset=None, **kwargs):
        return queryset.filter(is_deleted=False)

    @classmethod
    def search_code(cls, queryset, value):
        return queryset.filter(code__icontains=value)

    @classmethod
    def filter_query(cls, query_set, custom_search_fields=[]):
        return query_set.filter(is_deleted=False)

    @classmethod
    def get_default_custom_field_list(cls):
        return []

    @classmethod
    def run_post_processing_import(cls, items=[], user=None, organization=None, **kwargs):
        pass

    @classmethod
    def get_role_based_queryset(cls, queryset=None, request=None, user=None, **kwargs):
        if queryset is None:
            queryset = cls.objects.all()
        if user is None:
            request = CrequestMiddleware.get_request()
            user = request.c_user

        if user.is_super:
            return cls.get_queryset(queryset=queryset)

        cur_role = user.role
        class_name = cur_role.name
        while True:
            try:
                model = ContentType.objects.get(model=class_name.lower())
                break
            except:
                parent_roles = cur_role.parent.all()
                if parent_roles.exists():
                    cur_role = parent_roles.first()
                class_name = cur_role.name
                break

        try:
            user_role = get_model(model.app_label, class_name).objects.get(pk=user.pk)
        except:
            ConsoleUser = get_model('core', 'ConsoleUser')
            user_role = ConsoleUser.objects.get(pk=user.pk)

        queryset = cls.get_queryset(queryset=queryset, profile_filter=not (user.is_super))
        queryset = user_role.filter_model(request=request, queryset=queryset)
        # queryset = get_model(model.app_label, class_name).filter_model(request=request, queryset=queryset)
        if request:
            return SearchableModelMixin.apply_search_filter(request=request.GET, queryset=queryset)
        return queryset

    @classmethod
    def get_dependent_field_list(cls):
        return []

    def _get_pk_val(self, meta=None):
        _pk = super(DomainEntity, self)._get_pk_val(meta=meta)
        return None if _pk == 0 or _pk is None else _pk

    @classmethod
    def display_name(cls):
        name = cls.get_model_meta('route', 'display_name')
        if name is None:
            return bw_titleize(cls.__name__)
        return name

    @classmethod
    def get_import_model(cls):
        return cls

    @classmethod
    def get_export_dependant_fields(cls):
        return None

    @classmethod
    def get_serializer(cls):
        class DESerializer(serializers.ModelSerializer):

            def __init__(self, *args, fields=None, context=None, **kwargs):
                super().__init__(*args, context=context, **kwargs)

                if bool(context):
                    fields = context['request'].query_params.get('fields', None)
                    if bool(fields):
                        if isinstance(fields, tuple) or isinstance(fields, list):
                            pass
                        else:
                            fields = (fields,)

                        allowed = set(fields)
                        existing = set(self.fields.keys())
                        for field_name in existing - allowed:
                            self.fields.pop(field_name)

            def update(self, instance, validated_data):
                with transaction.atomic():
                    instance.last_updated_by = self.context['request'].c_user

                    # Before Updating the object create a new version of that object based on decorator and project settings
                    try:
                        instance.handle_version_creation()
                    except Exception as e:
                        _msg = "{} Version Couldn't Be Created. Error Message: {}".format(self.Meta.model.__name__, e)
                        from blackwidow.core.models import ErrorLog
                        ErrorLog.log(exp=_msg)
                    instance.last_updated_by = self.context['request'].c_user

                    m2m_fields = [
                        (f, f.model if f.model != self.Meta.model else None)
                        for f in self.Meta.model._meta.get_fields()
                        if f.many_to_many and not f.auto_created
                        ]
                    m2m_dict = dict()
                    for m in m2m_fields:
                        m2m_dict[m[0].name] = validated_data.pop(m[0].name, [])

                    attributes = self.Meta.model._meta.fields

                    for attr in attributes:
                        if attr.name in validated_data and isinstance(validated_data[attr.name], dict):
                            _obj = getattr(instance, attr.name)
                            if attr.name in [x[0] for x in self.Meta.model.get_custom_serializers()]:
                                _serializer = \
                                    list(filter(lambda a: a[0] == attr.name, self.Meta.model.get_custom_serializers()))[
                                        0][
                                        1](context=self.context)
                            else:
                                _serializer = attr.related_model.get_serializer()(context=self.context)

                            if _obj is None:
                                validated_data[attr.name] = _serializer.create(validated_data[attr.name])
                            else:
                                validated_data[attr.name] = _serializer.update(_obj, validated_data[attr.name])

                    for attr in attributes:
                        if attr.name in validated_data.keys():
                            if isinstance(attr, ForeignKey) or isinstance(attr, OneToOneField):
                                # _obj = getattr(instance, attr.name)
                                value = validated_data.pop(attr.name, None)
                                if isinstance(value, Model) and value.pk is None:
                                    value.save()
                                setattr(instance, attr.name,
                                        attr.model.objects.get(pk=value) if isinstance(value, int) else value)

                    for m in m2m_fields:
                        if m[0].name in m2m_dict.keys() and len(m2m_dict[m[0].name]) > 0:
                            _field = getattr(instance, m[0].name)
                            _values = m2m_dict[m[0].name]
                            if m[0].name in instance.__class__.get_dependent_field_list():
                                if isinstance(_values, User):
                                    _values.delete()
                                elif isinstance(_values, Model):
                                    temp = _values
                                    setattr(instance, m[0].name, None)
                                    instance.save()
                                    temp.delete(force_delete=True)
                                elif isinstance(_values, Manager):
                                    items = list(_values.all())
                                    _values.clear()
                                    for item in items:
                                        item.delete(force_delete=True)
                                else:
                                    pass

                            if m[0].name in [x for x in instance.__class__.get_dependent_field_list() if
                                             isinstance(getattr(instance, x), Manager)]:
                                _field.clear()
                            for v in _values:
                                if isinstance(v, (dict, OrderedDict)):
                                    if m[0].name in [x[0] for x in self.Meta.model.get_custom_serializers()]:
                                        _serializer = list(filter(lambda a: a[0] == m[0].name,
                                                                  self.Meta.model.get_custom_serializers()))[0][1](
                                            context=self.context)
                                    else:
                                        _serializer = m[0].related_model.get_serializer()(context=self.context)
                                    if isinstance(v, int):
                                        v = m[0].related_model.objects.get(pk=v)
                                    else:
                                        v = _serializer.create(v)

                                if m[0].name in [x[0] for x in self.Meta.model.intermediate_models()]:
                                    i_field = \
                                        list(
                                            filter(lambda x: x[0] == m[0].name, self.Meta.model.intermediate_models()))[
                                            0]
                                    setattr(v, i_field[3], instance)
                                    v.save()
                                else:
                                    v.save()
                                    _field.add(v)

                    response = super().update(instance, validated_data)

                    if hasattr(self.instance, 'create_version_if_needed'):
                        self.instance.create_version_if_needed()

                    return response

            def save(self, **kwargs):
                return super().save(**kwargs)

            def create(self, validated_data):
                with transaction.atomic():
                    tsync_id = validated_data.pop('tsync_id', uuid.uuid4())
                    responseObj = self.Meta.model.objects.filter(tsync_id=tsync_id)
                    if responseObj.exists():
                        return responseObj.first()

                    validated_data.update({
                        "created_by": self.context['request'].c_user,
                        "last_updated_by": self.context['request'].c_user,
                        "tsync_id": tsync_id
                    })

                    m2m_fields = [
                        (f, f.model if f.model != self.Meta.model else None)
                        for f in self.Meta.model._meta.get_fields()
                        if f.many_to_many and not f.auto_created
                        ]
                    m2m_dict = dict()
                    for m in m2m_fields:
                        m2m_dict[m[0].name] = validated_data.pop(m[0].name, [])

                    attributes = self.Meta.model._meta.fields

                    for attr in attributes:
                        if attr.name in validated_data and isinstance(validated_data[attr.name], dict):
                            if attr.name in [x[0] for x in self.Meta.model.get_custom_serializers()]:
                                _serializer = \
                                    list(filter(lambda a: a[0] == attr.name, self.Meta.model.get_custom_serializers()))[
                                        0][
                                        1](context=self.context)
                            else:
                                _serializer = attr.related_model.get_serializer()(context=self.context)
                            validated_data[attr.name] = _serializer.create(validated_data[attr.name])

                    pk = validated_data.pop('id', None)
                    if pk:
                        obj = self.Meta.model.objects.get(pk=pk)
                    else:
                        obj = self.Meta.model.objects.create(**validated_data)

                    for attr in attributes:
                        if isinstance(attr, ForeignKey) or isinstance(attr, OneToOneField):
                            value = validated_data.pop(attr.name, None)
                            if isinstance(value, Model) and value.pk is None:
                                value.save()
                            setattr(obj, attr.name,
                                    attr.model.objects.get(pk=value) if isinstance(value, int) else value)
                        else:
                            pass
                    obj.save()

                    for m in m2m_fields:
                        _field = getattr(obj, m[0].name)
                        _values = m2m_dict[m[0].name]
                        for v in _values:
                            if isinstance(v, (dict, OrderedDict)):
                                if m[0].name in [x[0] for x in self.Meta.model.get_custom_serializers()]:
                                    _serializer = \
                                        list(filter(lambda a: a[0] == m[0].name,
                                                    self.Meta.model.get_custom_serializers()))[
                                            0][1](context=self.context)
                                else:
                                    _serializer = m[0].related_model.get_serializer()(context=self.context)
                                v = _serializer.create(v)

                            if m[0].name in [x[0] for x in self.Meta.model.intermediate_models()]:
                                i_field = \
                                    list(filter(lambda x: x[0] == m[0].name, self.Meta.model.intermediate_models()))[0]
                                setattr(v, i_field[3], obj)
                                v.save()
                            else:
                                v.save()
                                _field.add(v)

                    if hasattr(obj, 'create_version_if_needed'):
                        obj.create_version_if_needed()

                    return obj

            def mutate(self, **kwargs):
                self.instance = self.instance.mutate_to()
                return self.instance

            class Meta:
                model = cls
                read_only_fields = (
                    'created_by', 'code', 'type', 'id', 'last_updated', 'date_created', 'last_updated_by',
                    'is_active', 'is_deleted', 'is_locked', 'timestamp')

        return DESerializer

    def load_initial_data(self, **kwargs):
        self.created_by = kwargs['user']
        self.last_updated_by = kwargs['user']
        self.date_created = kwargs['timestamp']
        self.last_updated = kwargs['timestamp']

    @classmethod
    def init_default_objects(cls, count=1, user=None, organization=None, class_name=None, **kwargs):
        if user is None:
            user = get_model('core', 'ConsoleUser').objects.filter(is_super=True).first()
        if organization is None:
            organization = get_model('core', 'Organization').objects.filter(is_super=True).first()

        context = dict(
            request=HttpRequest()
        )
        context['request'].c_user = user
        context['request'].QUERY_PARAMS = dict()

        attributes = cls._meta.fields
        attributes = [x for x in attributes if x.name not in cls.get_system_fields()]
        _get_m2m_with_model = [
            (f, f.model if f.model != cls else None)
            for f in cls._meta.get_fields()
            if f.many_to_many and not f.auto_created
            ]
        m2m_attributes = [x[0] for x in _get_m2m_with_model]

        objs = list()
        for _index in range(0, count):
            with transaction.atomic():
                attrs = dict()
                for attr in attributes:
                    from blackwidow.core.models.file.fileobject import FileObject

                    field = cls._meta.get_field(attr.name)
                    if isinstance(field, models.AutoField):
                        pass
                    elif isinstance(field, models.ForeignKey):
                        _model = attr.related_model
                        if attr.name == 'organization':
                            attrs[attr.name] = organization
                        elif attr.name == 'created_by':
                            attrs[attr.name] = user
                        elif attr.name == 'last_updated_by':
                            attrs[attr.name] = user
                        elif attr.model == attr.related_model:
                            pass
                        elif issubclass(attr.related_model, FileObject):
                            pass
                        elif attr.name in cls.get_dependent_field_list():
                            if attr.name not in cls.get_system_fields():
                                attrs[attr.name] = \
                                    _model.init_default_objects(count=1, class_name=_model.__name__, user=user,
                                                                organization=organization)[0]
                        else:
                            if not _model.objects.exists():
                                attrs[attr.name] = \
                                    _model.init_default_objects(count=1, user=user, class_name=_model.__name__,
                                                                organization=organization)[0]
                            else:
                                attrs[attr.name] = _model.objects.filter(type=_model.__name__).first()
                    elif isinstance(field, models.ManyToManyField):
                        _model = attr.related_model
                        if attr.name in cls.get_dependent_field_list():
                            attrs[attr.name] = _model.init_default_objects(count=1, user=user,
                                                                           organization=organization)
                        else:
                            pass
                    elif isinstance(field, models.DecimalField):
                        attrs[attr.name] = random.randrange(0, 9999) / 100
                    elif isinstance(field, (models.BigIntegerField, models.IntegerField)):
                        attrs[attr.name] = random.randrange(0, 99)
                    elif isinstance(field, models.BooleanField):
                        if attr.name == 'is_active':
                            attrs[attr.name] = True
                        else:
                            attrs[attr.name] = False
                    elif isinstance(field, models.FileField):
                        attrs[attr.name] = None
                    elif isinstance(field, models.CharField):
                        attrs[attr.name] = ''.join(
                            random.choice(string.ascii_letters) for i in range(random.randrange(12, 20)))
                    else:
                        print('Unidentified field - ' + attr.name)

                for attr in m2m_attributes:
                    if attr.name in cls.get_dependent_field_list():
                        pass
                        # attrs[attr.name] = attr.related.model.init_default_objects(count=1, user=user, organization=organization)
                    else:
                        pass

                if class_name is not None:
                    attrs['type'] = class_name

                obj = cls.get_serializer()(context=context).create(attrs)
                objs.append(obj)
        return objs

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], include_m2m=True, **kwargs):
        _nkwargs = copy.deepcopy(kwargs)
        if kwargs.get('output', '') == 'str':
            fields = self.serializable_fields
            if len(fields) > 0:
                kwargs.update({
                    'fields': fields
                })
            return serializers.serialize('json', [self], **kwargs)
        elif kwargs.get('output', 'json') == 'json':
            attributes = self._meta.fields
            if len(self.serializable_fields) > 0:
                attributes = [x for x in attributes if x.name in self.serializable_fields]
            if _nkwargs.get('system', 0) == 0:
                attributes = [x for x in attributes if x.name not in self.__class__.get_system_fields()]
            if include_m2m:
                m2m_attributes = [x[0] for x in
                                  [(f, f.model if f.model != self else None) for f in self._meta.get_fields()
                                   if f.many_to_many and not f.auto_created]]
            else:
                m2m_attributes = list()
            obj = dict()
            for attr in attributes:
                if (attr.many_to_one or attr.one_to_one) and depth == 0:
                    try:
                        value = getattr(self, str(attr.name) + '_id')
                        obj[attr.name] = value
                    except:
                        pass
                else:
                    value = getattr(self, attr.name)
                    if isinstance(value, datetime.datetime):
                        obj[attr.name] = value.isoformat(' ')
                        obj[attr.name + '_unix'] = (value).timestamp() * 1000
                    elif isinstance(value, DomainEntity):
                        _wrapper = [x for x in wrappers if x[0] == value.__class__]
                        _conditional_expand = []
                        for x in conditional_expand:
                            if x[0] == self.__class__:
                                _conditional_expand = x[1]
                        if (expand is None and depth > 0) or (
                                        expand is not None and attr.name in expand) or attr.name in _conditional_expand:
                            if len(_wrapper) > 0:
                                obj[attr.name] = \
                                    _wrapper[0][1].wrap([value.to_json(depth=depth - 1, expand=expand, **_nkwargs)])[0]
                            else:
                                obj[attr.name] = value.to_json(depth=depth - 1, expand=expand, **_nkwargs)
                        else:
                            obj[attr.name] = value.pk
                    elif isinstance(value, Model):
                        pass
                    elif isinstance(value, Decimal):
                        obj[attr.name] = float(value)
                    elif isinstance(value, list):
                        _wrapper = [x for x in wrappers if x[0] == value.__class__]
                        if (expand is None and depth > 0) or (expand is not None and attr.name in expand):
                            if len(_wrapper) > 0:
                                obj[attr.name] = _wrapper[0][1].wrap(
                                    [x.to_json(depth=depth - 1, expand=expand, **_nkwargs) for x in value.all()])
                            else:
                                obj[attr.name] = value.to_json(depth=depth - 1, expand=expand, **_nkwargs)
                        else:
                            obj[attr.name] = [x.pk for x in value.all()]
                    else:
                        obj[attr.name] = value if value is not None else ''

            for attr in m2m_attributes:
                value = getattr(self, attr.name)
                if (expand is None and depth > 0) or (expand is not None and attr.name in expand):
                    obj[attr.name] = [x.to_json(depth=depth - 1, expand=expand, **_nkwargs) for x in value.all()]
                else:
                    obj[attr.name] = [x.pk for x in value.all()]
            return obj
        return None

    @classmethod
    def get_model_data_query(cls):
        return Q(is_deleted=False)

    def to_model_data(self):
        model_data = dict()
        model_data['id'] = self.pk
        model_data['code'] = self.code
        return model_data

    @classmethod
    def get_relational_data_configs(cls):
        return []

    def get_choice_name(self):
        return self.code

    def get_audit_log_model_name(self):
        try:
            return self.type
        except:
            return self.__class__.__name__

    def app_assignment(self, **kwargs):
        pass

    @classmethod
    def get_trigger_properties(cls, prefix='', expand=[]):
        fields = []
        _fields = cls._meta.fields
        for f in _fields:
            if f.name in expand:
                fields += f.related_model._meta.model.get_trigger_properties(prefix=prefix + f.name + "__")
            else:
                fields.append(prefix + f.name)
        return fields

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        request = CrequestMiddleware.get_request()
        with transaction.atomic():
            self.clean()
            if self.pk is None:
                self.type = self.__class__.__name__ if self.type == '' else self.type

            if self.date_created is None or self.date_created == 0:
                self.date_created = Clock.timestamp()
                if self.created_by is None:
                    try:
                        self.created_by = request.c_user
                    except:
                        pass
            self.tsync_id = uuid.uuid4() if self.tsync_id is None else self.tsync_id
            self.last_updated = Clock.timestamp()
            try:
                self.last_updated_by = request.c_user
            except:
                pass
            super(DomainEntity, self).save()
            if not self.code:
                self.code = self.code_prefix + self.code_separator + str(self.id).zfill(5)
                super().save()
            self.save_assignment_log()
        if self._meta.proxy:
            post_save.send(sender=super(DomainEntity, self).__class__, instance=self)

    def delete(self, *args, force_delete=False, user=None, **kwargs):
        with transaction.atomic():
            _through_fields = []
            if len(self.__class__.get_dependent_field_list()) > 0:
                for field_name in self.__class__.get_dependent_field_list():
                    field = getattr(self, field_name)
                    if isinstance(field, User):
                        if force_delete:
                            field.delete()
                    elif isinstance(field, Model):
                        temp = field
                        setattr(self, field_name, None)
                        self.save()
                        temp.delete(*args, user=user, force_delete=force_delete, **kwargs)
                    elif isinstance(field, Manager):
                        items = list(field.all())
                        field.clear()
                        for item in items:
                            item.delete(*args, user=user, force_delete=force_delete, **kwargs)
                    else:
                        pass
            if not force_delete or user.is_super is False:
                references = []
                _get_all_related_objects = [f for f in self._meta.get_fields() if
                                            (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete]
                for robject in _get_all_related_objects:
                    if robject is not None:
                        q = Q(**{"%s__id" % robject.field.name: self.id})
                        _len = len(robject.related_model.objects.filter(q))
                        if _len > 0:
                            references.append('<li><strong>' + str(_len) + '</strong>: ' + bw_titleize(
                                robject.model.__name__) + '(s) </li>')
                if len(references) > 0:
                    references = ['Item is referred by - '] + ['<ul>'] + references + ['</ul>'] + [
                        'Please remove the referrer items before deleting this item.']
                    raise EntityNotDeletableException(''.join(references))
            super(DomainEntity, self).delete(*args, **kwargs)

    class Meta:
        abstract = True
