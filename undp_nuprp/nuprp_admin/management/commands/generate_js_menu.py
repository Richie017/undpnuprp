from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from blackwidow.core.views.menu.menu_renderer_view import MenuRendererView

get_model = apps.get_model

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def generate_js_menu(self, *args, **kwargs):
        Role = get_model('core', 'Role')
        all_roles = Role.objects.all()

        # checking js menu rendering is enable or not, if enabled then generate js menu config for roles
        if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
            print("Generating JS Menu for -->")
            for _role in all_roles:
                MenuRendererView.save_role_menu_config(role=_role)

    def handle(self, *args, **options):
        actions = [self.generate_js_menu, ]
        i = 1
        total_step = len(actions)
        for a in actions:
            self.stdout.write("step: " + str(i) + "/" + str(total_step))
            a(*args, **options)
            self.stdout.write('\n')
            i += 1
