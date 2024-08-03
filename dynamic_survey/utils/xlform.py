import json
import os
import subprocess

from django.conf import settings

PROJECT_ROOT = settings.PROJECT_PATH
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'dynamic_survey', 'static')

def split_apart_survey(scsv, **opts):
    opts['action'] = 'split_into_individual_surveys'
    return process_xlform(scsv, **opts)


def shrink_survey(scsv):
    return process_xlform(scsv, action='shrinkSurvey')


def summarize_survey(scsv):
    return process_xlform(scsv, action='summarizeSurvey')


def process_xlform(pp, **opts):
    jsargs = ["node", os.path.join(STATIC_ROOT, "jsapp/utils/process_xlform.js")]
    for key, val in opts.items():
        if type(val) is dict:
            val = "'%s'" % (json.dumps(val).replace("'", "\\'"))
        jsargs.append("--%s=%s" % (key, val))
    xlf_proccess = subprocess.Popen(jsargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    xlf_proccess.stdin.write(pp)
    try:
        p_resp = json.loads(xlf_proccess.communicate()[0])
        if type(p_resp) == dict and p_resp.has_key('error'):
            raise XlformError(p_resp.get('error'))
    except ValueError as e:
        raise XlformError(e)
    return p_resp


class XlformError(Exception):
    pass
