"""
WSGI config for blackwidow project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "blackwidow.settings"

# SUB_SITE = 'uttara/'
# LOGIN_URL = '/uttara/account/login'
#
#
# settings.STATICFILES_DIRS = (
#     # Put strings here, like "/home/html/static" or "C:/www/django/static".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     dict(name='blackwidow_static', sub_site=SUB_SITE, path=os.path.join(settings.PROJECT_PATH, "themes/" + settings.CURRENT_THEME + "/static/")),
#     dict(name='blackwidow_libs', sub_site=SUB_SITE, path=os.path.join(settings.PROJECT_PATH, "blackwidow/libs/")),
# )

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"


# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

"""The following section is for newrelic. To disable newrelic, comment out this part"""
# import newrelic.agent
# newrelic.agent.initialize(os.path.join(os.path.dirname(__file__), "newrelic.ini"))
# application = newrelic.agent.WSGIApplicationWrapper(application)
# End of new relic config

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
