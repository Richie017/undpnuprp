from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Ziaul Haque'

MODULE_TITLES = {
    'Reporting': 'Dashboard',
    'Interactive Map': 'Interactive Map',
    'Analysis': 'Entry',
    'Targets': 'Targets',
    'Alerts': 'Alerts',
    'CRM': 'CRM',
    'Infrastructure': 'Infrastructure',
    'Users & Clients': 'Users & Clients',
    'Execute': 'Approvals',
    'Administration': 'Survey Admin',
    'Inventory': 'Inventory',
    'Settings': 'Admin',
    'Help': 'Help',
    'Maintenance': 'Maintenance',
    'Demo Intro': 'Demo Intro',
    'Surveys': 'Survey',
    "DeviceManager": "Documents"
}

# please update url mapping according to project requirement
MODULE_URLS = {
    ModuleEnum.Administration.value['route']: 'survey',
    ModuleEnum.Execute.value['route']: 'pending-scg-monthly-report',
    ModuleEnum.Survey.value['route']: 'surveys',
    ModuleEnum.Reports.value['route']: 'pg-member-information-indicators',
    ModuleEnum.Analysis.value['route']: 'primary-groups',
    ModuleEnum.Settings.value['route']: 'roles',
    ModuleEnum.DeviceManager.value['route']: 'upload-files',
    ModuleEnum.Alert.value['route']: 'duplicate-id-alerts',
    ModuleEnum.InteractiveMap.value['route']: 'sif-interventions-map'
}
