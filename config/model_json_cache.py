from settings import STATICFILES_DIRS, STATIC_URL

__author__ = 'Shamil'

MODEL_JASON_DIR = STATICFILES_DIRS[0] + 'model_data/'
MODEL_JASON_URL = STATIC_URL + 'model_data/'

MENU_JSON_DIR_SUFFIX = '/model_data/'
MENU_JASON_FILE_SUFFIX = '-menus.js'

ENABLE_JS_MENU_RENDERING = True  # set True to enable js menu rendering
