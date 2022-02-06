from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.models.roles.role import Role

__author__ = 'ruddra'

other_user_config = dict(
                name ='Other User',
                id = 9999,
                role = Role.objects.get(name='Aparajita'),
                organization = Organization.objects.filter(is_master=True)[0],
                )