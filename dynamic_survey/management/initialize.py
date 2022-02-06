"""This module is the app specific initialization module. In the `initialize` method it does all the
   app specific tasks. The `initialize` command is called when `bw_init_data` command is run.
   Take a look at the docstring of `initialize` method
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from blackwidow.core.models import Organization, ErrorLog, ApprovalProcess, ApprovalAction, ApprovalStatus, \
    ApprovalLevel, Role, ConsoleUser
from blackwidow.core.models.roles.developer import Developer
from blackwidow.core.models.users.system_admin import SystemAdmin

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.design.dynamic_survey_group import DynamicSurveyGroup

__author__ = 'Razon'



@transaction.atomic
def create_approval_process():
    """
    This function does the following tasks:
    1. Finds a super user if any otherwise returns from the function
    2. Finds an organization if any otherwise returns from the function
    3. Finds a ApprovalProcess for `DynamicSurvey` model. If it already exist it returns from the function.
       Otherwise it creates the `ApprovalProcess` on `DynamicSurvey` model under super user and the organization
       from step 1 and 2.
    4. Then It creates an `ApprovalLevel` with `level`: 1, 'approve_model': `DynamicSurvey`,
       'reject_model': `DynamicSurvey` , `roles`: ['SystemAdmin', 'Developer'] under super user
       and the organization from step 1 and 2. And then the `ApprovalLevel` is added to the `ApprovalProcess`.

    :return: None
    """
    print("\nTask: 1\n")

    try:
        super_user = ConsoleUser.objects.filter(is_super=True).first()
    except ConsoleUser.DoesNotExist as e:
        print("Super User Doesn't Exist. Create A Super User First")
        print(e)
        ErrorLog.log(exp=e)
        return

    try:
        organization = Organization.objects.first()
    except Organization.DoesNotExist as e:
        print("Organization Doesn't Exist. Create An Organization First")
        print(e)
        ErrorLog.log(exp=e)
        return

    try:
        survey_approval_process, created = ApprovalProcess.objects.get_or_create(
            model_name=DynamicSurvey.__name__,
            organization_id=organization.pk)
    except Exception as e:
        print("There Might Be Several Approval Processes Already Exist For DynamicSurvey Model. Checkout The Error.")
        print(e)
        ErrorLog.log(exp=e)
        return

    if created:
        print("Step : 1")
        print("Creating Survey Approval Process...")
        survey_approval_process.created_by = super_user
        survey_approval_process.last_updated_by = super_user
        survey_approval_process.save()

        print("\nStep : 2")
        print("Creating Approval Level...")
        try:
            approval_level = ApprovalLevel()
            approval_level.organization_id = organization.pk
            approval_level.level = 1
            approval_level.approve_model = DynamicSurvey.__name__
            approval_level.reject_model = DynamicSurvey.__name__
            approval_level.created_by = super_user
            approval_level.last_updated_by = super_user
            approval_level.save()
            print("\nStep : 3")
            print("Getting The Initial Roles...")
            initial_approved_roles = []
            initial_approved_role_classes = [SystemAdmin, Developer]

            for r in initial_approved_role_classes:
                initial_approved_roles.append(r.get_model_meta('route', 'display_name') or r.__name__)

            roles = Role.objects.filter(name__in=initial_approved_roles)
            roles = list(roles)
            print("\nStep : 4")
            print("Adding The Roles To Approval Level...")
            approval_level.roles.add(*roles)
            print("\nStep : 5")
            print("Adding The Approval Level To The Approval Process...")
            survey_approval_process.levels.add(approval_level)
        except Exception as e:
            print("Exception In Approval Level Creation.")
            print(e)
            ErrorLog.log(exp=e)
            return
    else:
        print("Survey Approval Process Exists ... Skiping")


@transaction.atomic
def create_sample_survey():
    """
    This function does the following tasks:
    1. Finds a super user if any otherwise returns from the function
    2. Finds an organization if any otherwise returns from the function
    3. Finds approval process for `DynamicSurvey` model if any otherwise returns from the function
    4. Creates a sample survey from a string
    5. Creates an `ApprovalAction` for the currently saved survey object and the action is added to survey
       approval process.

    :return: None
    """
    print("\nTask: 2\n")

    if DynamicSurveyGroup.objects.exists():
        # TODO: When should I actually show a sample survey
        print("Sample Survey Already Exists ... Skipping")
        return

    try:
        super_user = ConsoleUser.objects.filter(is_super=True).first()
    except ConsoleUser.DoesNotExist as e:
        print("Super User Doesn't Exist. Create A Super User First")
        print(e)
        ErrorLog.log(exp=e)
        return

    print("Step: 1")
    print("Getting The Organization...")
    # Now finding the organization id to get the approval process
    try:
        organization = Organization.objects.first()

    except Organization.DoesNotExist as e:
        print("Organization Doesn't Exist. Create An Organization First")
        print(e)
        ErrorLog.log(exp=e)
        return

    _csv = '''"survey",,,,,,,,,,
,"name","type","label","hint","required","default","constraint","relevant","appearance","constraint_message"
,"group_pv6qg01","begin group","Personal Questionnaire",,,,,,,
,"What_is_your_name","text","What is your name?","In Block Letters","true","John Doe",". !=  'Justin Bieber' and . !=  'Imrul Kayes'",,,
,"What_is_your_age","integer","What is your age?","Enter an integer, we are not interested in months and days","true","18",". >= 18 and . <= 100","${What_is_your_name} != ''",,
,"What_is_your_phone_number","integer","What is your phone number?","No need to add country code","false",,,"${What_is_your_name} != '' and ${What_is_your_age} >= 18 and ${What_is_your_age} <= 100",,
,"What_is_your_religion","free_choice_field pf2he36","What is your religion?",,"true",,,"${What_is_your_age} >= 18",,
,"What_is_your_favorite_color","select_one jp4da15","What is your favorite color?",,"true",,,,,
,"Which_are_your_favorite_TV_ser","select_multiple uj9bp55","Which are your favorite TV series?",,"true",,,"not(selected(${What_is_your_religion}, 'islam'))",,
,,"end group",,,,,,,,
,"group_jw0rt21","begin group","Life Related Questionnaire",,,,,,,
,"How_is_life","select_one js0mm72","How is life?",,"true",,,,,
,"How_was_childhood","select_one rd2es77","How was childhood",,"true",,,,,
,,"end group",,,,,,,,
,"start","start",,,,,,,,
,"end","end",,,,,,,,
"choices",,,
,"label","name","list name"
,"Islam","islam","pf2he36"
,"Hinduism","hinduism","pf2he36"
,"Christianism","christianism","pf2he36"
,"Atheism","atheism","pf2he36"
,"Agnosticism","agnosticism","pf2he36"
,"Other","other","pf2he36"
,"Red","red","jp4da15"
,"Blue","blue","jp4da15"
,"White","white","jp4da15"
,"Black","black","jp4da15"
,"Green","green","jp4da15"
,"Violet","violet","jp4da15"
,"Game Of Thrones","game_of_throne","uj9bp55"
,"Breaking Bad","breaking_bad","uj9bp55"
,"Fargo","fargo","uj9bp55"
,"Friends","friends","uj9bp55"
,"Dexter","dexter","uj9bp55"
,"Prison Break","prison_break","uj9bp55"
,"Sherlock","sherlock","uj9bp55"
,"Band Of Brothers","band_of_brothe","uj9bp55"
,"Beautiful","beautiful","js0mm72"
,"Good","good","js0mm72"
,"Not Bad","not_bad","js0mm72"
,"Bad","bad","js0mm72"
,"Poor","poor","js0mm72"
,"Good","good","rd2es77"
,"Bad","bad","rd2es77"
"settings",,
,"form_title","form_id"
,"Sample Survey","sample_survey"'''
    print("\nStep: 2")
    print("Getting The Approval Process...")
    # Now we are making sure the approval process for the corresponding database is created or not
    try:
        survey_approval_process = ApprovalProcess.objects.filter(
            model_name=DynamicSurvey.__name__,
            organization_id=organization.pk).first()
    except ApprovalProcess.DoesNotExist as e:
        print("Approval Process For `DynamicSurvey` Model Doesn't Exist. Create The Approval Process First.")
        print(e)
        ErrorLog.log(exp=e)
        return

    print("\nStep: 3")
    print("Creating Sample Survey Group...")
    # Create a survey object first
    try:
        new_name = "Sample Survey Group"
        survey = DynamicSurveyGroup(group_name=new_name, organization=organization)
        survey.created_by = super_user
        survey.last_updated_by = super_user
        survey.save()
    except Exception as e:
        print("Exception In Survey Group Creation.")
        print(e)
        ErrorLog.log(exp=e)
        return

    print("\nStep: 4")
    print("Creating Sample Survey...")
    # Then create the survey draft object and keep a reference of survey object there
    try:
        from django.contrib.auth.models import User
        new_survey_draft = DynamicSurvey.objects.create(**{
            'body': str(_csv),
            'name': "Sample Survey",
            'user': super_user.user,
            'organization': organization
        })
        new_survey_draft.detail_link = str(new_survey_draft)
        new_survey_draft.survey_id = survey.id
        new_survey_draft.created_by = super_user
        new_survey_draft.last_updated_by = super_user
        new_survey_draft.save()
    except Exception as e:
        print("Exception In Sample Survey Creation")
        print(e)
        ErrorLog.log(exp=e)
        return

    print("\nStep: 5")
    print("Creating The Approval Action...")
    try:
        approval_action = ApprovalAction(organization=organization)
        approval_action.model_name = DynamicSurvey.__name__
        approval_action.status = ApprovalStatus.Approved.value
        approval_action.object_id = new_survey_draft.id
        approval_action.level = 0
        approval_action.created_by = super_user
        approval_action.last_updated_by = super_user
        approval_action.save()
    except Exception as e:
        print("Exception In Approval Action Creation")
        print(e)
        ErrorLog.log(exp=e)
        return
    print("\nStep: 6")
    print("Adding The Approval Action To The Approval Process")
    # Now this approval action is being added to the corresponding approval process
    try:
        survey_approval_process.actions.add(approval_action)
    except Exception as e:
        print("Exception In Adding Approval Action To Approval Process")
        print(e)
        ErrorLog.log(exp=e)
        return


def initialize(*args, **kwargs):
    actions = [
        create_approval_process,
        create_sample_survey
    ]

    i = 1
    for a in actions:
        a(*args, **kwargs)
        i += 1
    print('-------successfully completed-------')
