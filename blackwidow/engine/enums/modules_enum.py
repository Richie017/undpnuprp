from enum import Enum

__author__ = 'Mahmud'


class ModuleEnum(Enum):
    Reports = {
        'title': "Reporting",
        'route': 'reports',
        "icon": "fbx-report",
        'order': 0
    }
    InteractiveMap = {
        'title': "Interactive Map",
        'route': 'interactive-maps',
        "icon": "fbx-target",
        'order': 2
    }
    Analysis = {
        'title': "Analysis",
        'route': 'analysis',
        "icon": "fbx-target",
        'order': 5
    }
    Targets = {
        'title': "Targets",
        'route': 'kpi',
        "icon": "î‚¶",
        'order': 10
    }
    Alert = {
        'title': "Alerts",
        'route': 'communication',
        "icon": "fbx-alerts",
        'order': 15
    }
    CRM = {
        'title': "CRM",
        'route': 'crm',
        "icon": "î„›",
        'order': 20
    }
    Infrastructure = {
        'title': 'Infrastructure',
        'route': 'infrastructure',
        "icon": "î‡�",
        'order': 25
    }
    Users = {
        'title': "Users & Clients",
        'route': 'users',
        "icon": "î�±",
        'order': 30
    }
    Execute = {
        'title': "Execute",
        'route': 'execute',
        "icon": "fbx-task",
        'order': 34
    }
    Administration = {
        'title': "Administration",
        'route': 'administration',
        "icon": "fbx-admin",
        'order': 35
    }
    Inventory = {
        'title': "Inventory",
        'route': 'inventory',
        "icon": "î„›",
        'order': 40
    }
    ImportExport = {
        'title': "Import/Export",
        'route': 'import-export',
        "icon": "î„›",
        'order': 97
    }
    Settings = {
        'title': "Settings",
        'route': 'settings',
        "icon": "fbx-settings",
        'order': 98
    }
    Help = {
        'title': "Help",
        'route': 'help',
        "icon": "î‚“",
        'order': 99
    }
    Maintenance = {
        'title': "Maintenance",
        'route': 'maintenance',
        "icon": "î‚“",
        'order': 100
    }
    DemoIntro = {
        'title': 'Demo Intro',
        'route': 'demo_intro',
        'icon': 'i',
        'order': 105
    }
    Survey = {
        'title': 'Surveys',
        'route': 'surveys',
        'icon': 'i',
        'order': 110
    }
    DeviceManager = {
        'title': "DeviceManager",
        'route': 'device-manager',
        "icon": "fbx-target",
        'order': 100
    }