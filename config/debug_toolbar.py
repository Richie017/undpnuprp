__author__ = 'Mahmud'


# debug_toolbar settings
# if DEBUG:
#     INTERNAL_IPS = ('127.0.0.1',)
#     MIDDLEWARE_CLASSES += (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     )
#
#     INSTALLED_APPS += (
#         'debug_toolbar',
#     )
#
#     DEBUG_TOOLBAR_PANELS = [
#         'debug_toolbar.panels.versions.VersionsPanel',
#         'debug_toolbar.panels.timer.TimerPanel',
#         'debug_toolbar.panels.settings.SettingsPanel',
#         'debug_toolbar.panels.headers.HeadersPanel',
#         'debug_toolbar.panels.request.RequestPanel',
#         'debug_toolbar.panels.sql.SQLPanel',
#         'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#         'debug_toolbar.panels.templates.TemplatesPanel',
#         'debug_toolbar.panels.cache.CachePanel',
#         'debug_toolbar.panels.signals.SignalsPanel',
#         'debug_toolbar.panels.logging.LoggingPanel',
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#         ]
#
#     DEBUG_TOOLBAR_CONFIG = {
#         'INTERCEPT_REDIRECTS': False,
#     }
#
#     CONFIG_DEFAULTS = {
#         # Toolbar options
#         'RESULTS_STORE_SIZE': 3,
#         'SHOW_COLLAPSED': True,
#         # Panel options
#         'INTERCEPT_REDIRECTS': True,
#         'SQL_WARNING_THRESHOLD': 100,   # milliseconds
#     }