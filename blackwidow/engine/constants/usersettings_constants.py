__author__ = 'Mahmud'

BWSETT_NOTIFICATION_SMS = 'enable_sms_notification'
BWSETT_NOTIFICATION_EMAIL = 'enable_email_notification'
BWSETT_NOTIFICATION_WEB = 'enable_web_notification'

BWCONST_ALLOWABLE_USER_SETTINGS = dict(
    allow_duplicates=False,
    keys=list())

BWCONST_ALLOWABLE_USER_SETTINGS['keys'].append(dict(
            name=BWSETT_NOTIFICATION_EMAIL,
            display='Enable Email Notification',
            type='boolean',
            default='False',
            range=set(['True', 'False']),
            dbkey=BWSETT_NOTIFICATION_EMAIL
        ))

BWCONST_ALLOWABLE_USER_SETTINGS['keys'].append(dict(
            name=BWSETT_NOTIFICATION_SMS,
            display='Enable SMS Notification',
            type='boolean',
            default='False',
            range=set(['True', 'False']),
            dbkey=BWSETT_NOTIFICATION_SMS
        ))

BWCONST_ALLOWABLE_USER_SETTINGS['keys'].append(dict(
            name=BWSETT_NOTIFICATION_WEB,
            display='Enable Web Notification',
            type='boolean',
            default='False',
            range=set(['True', 'False']),
            dbkey=BWSETT_NOTIFICATION_WEB
        ))






