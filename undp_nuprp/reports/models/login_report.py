from blackwidow.core.models import ConsoleUser
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='login-report', group='Reports', group_order=3, module=ModuleEnum.Reports,
                display_name="User Login Report", hide=True))
class UserLoginReport(Report):
    class Meta:
        proxy = True

    @classmethod
    def build_report(cls, role_filter=None, console_users=None, time_from=None, time_to=None, styled=False):
        queryset = ConsoleUser.objects.all().order_by('-user__last_login')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        if console_users:
            queryset = queryset.filter(pk__in=console_users)

        if time_from is not None and time_to is not None:
            queryset = queryset.filter(user__last_login__range=(time_from, time_to))

        report = []

        headers = ['User', 'Role', 'Username', 'Last Login Time', 'Working Area Hierarchy']
        if styled:
            report.append(tuple(headers))
        else:
            report.append(headers)

        for _obj in queryset:
            _role = _obj.role
            _user = _obj
            _last_login_time = _obj.render_timestamp(_obj.user.last_login.timestamp() * 1000)
            _working_area_hierarchy = _obj.render_assignment_hierarchy
            row = cls.generate_table_row(
                styled=styled,
                user=_user,
                role=_role,
                login_name=_obj.user.username,
                last_login_time=_last_login_time,
                working_area_hierarchy=_working_area_hierarchy
            )

            report.append(row)
        return report

    @classmethod
    def generate_table_row(cls, styled, last_login_time, user, login_name, role, working_area_hierarchy):
        if styled:
            row = (
                user.__str__(),
                role.__str__(),
                login_name,
                last_login_time,
                working_area_hierarchy
            )
        else:
            row = [
                user.code + ": " + user.name,
                role.code + ": " + role.name,
                login_name,
                last_login_time,
                working_area_hierarchy
            ]
        return row
