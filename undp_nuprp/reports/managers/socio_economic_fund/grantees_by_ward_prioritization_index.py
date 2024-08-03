
import math
from django.db.models import Sum, F
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import Q

from blackwidow.core.models import Geography
from blackwidow.core.models.clients.client import Client
from undp_nuprp.approvals.models import Intervention
from undp_nuprp.approvals.models import WordPrioritizationIndicator

from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.reports.models import SEFGranteesInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
from collections import OrderedDict

__author__ = 'Ahsan@4Axiz'


def get_grantees_by_ward_prioritization_index_table_data(towns=list):


    wards = dict()
    wards = Geography.objects.filter(type='Ward')
    print('Print test')
    print(wards)
    grantee_wise_installment_dict = OrderedDict()
    response_data = []
    header_row = ['City Corporation/Pourosova', 'Ward No', 'Ward Prioritization Index',
    'No. of Total Grantee-SEF', 'No. of Total Grantee-Nutrition', 'No. of Grantee-SIF', 'No. of Grantee-CRMIF',
    'Total Grantee']
    grantee_wise_installment_dict['total_sef'] = 0
    grantee_wise_installment_dict['total_nutrition'] = 0
    grantee_wise_installment_dict['total_sif'] = 0
    grantee_wise_installment_dict['total_crmif'] = 0
    grantee_wise_installment_dict['total_grantee'] = 0

    response_data.append(header_row)

    
    for ward in wards:
        
        # print(city[0].name)

        # Ward Name
        ward_name= ward.name
        ward_id= ward.id

        # City Name
        city = Geography.objects.filter(id=ward.parent_id)
        city_id = city[0].id
        city_name = city[0].name
        ward_poverty_index = ""
        # Ward Poverty Index(WPI)
        query = WordPrioritizationIndicator.objects.filter(Ward_id=ward_id).values('poverty_index_quantile', 'total_population')
        for b in query:
            if b['poverty_index_quantile']:
                ward_poverty_index = "Q"+str(b['poverty_index_quantile'])
            else:
                ward_poverty_index = ""
        # print("Query")
        # print(query)

        
        
        ## No Of grantees SEF
        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).exclude(ward=None).values('city_id', 'ward')
        ng = queryset.filter(city_id=city_id, ward=ward_name)\
            .annotate(Sum('no_of_business_grantee'),
                      Sum('no_of_apprenticeship_grantee'),
                      Sum('no_of_education_dropout_grantee'),
                      Sum('no_education_early_marriage_grantee'),
                      Sum('no_of_nutrition_grantees')
            )
        # No of nutrition grantees
        nTotal = 0
        total = 0
        for n in ng:
            if n['ward']:
                nTotal = n['no_of_nutrition_grantees__sum']
                if n['no_of_business_grantee__sum']:
                    total += n['no_of_business_grantee__sum']
                if n['no_of_apprenticeship_grantee__sum']:
                    total += n['no_of_apprenticeship_grantee__sum']
                if n['no_of_education_dropout_grantee__sum']:
                    total += n['no_of_education_dropout_grantee__sum']
                if n['no_education_early_marriage_grantee__sum']:
                    total += n['no_education_early_marriage_grantee__sum']
        total_no_of_grantee_sef = total

        total_no_of_nutrition_grantees = nTotal


        ## No Of grantees SIF
        queryset = Intervention.objects.filter(
            sif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.SIF'
        ).distinct().values(
            'sif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
       
        tSIF = 0
        for q in queryset:
            if q['number_of_total_pg_member_beneficiary__sum']:
                tSIF = q['number_of_total_pg_member_beneficiary__sum']
            if q['number_of_total_non_pg_member_beneficiary__sum']:
                tSIF += q['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_sif_grantees = tSIF
     
        ## No Of grantees CRMIF
        queryset = Intervention.objects.filter(
            crmif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.CRMIF'
        ).distinct().values(
            'crmif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
        # print(queryset)
        tCRMIF = 0
        if queryset.count()>0:
            if queryset[0]['number_of_total_pg_member_beneficiary__sum']:
                tCRMIF = queryset[0]['number_of_total_pg_member_beneficiary__sum']
            if queryset[0]['number_of_total_non_pg_member_beneficiary__sum']:
                tCRMIF += queryset[0]['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_crmif_grantees = tCRMIF

        ## Total grantee
        total_grantee = total_no_of_grantee_sef + total_no_of_nutrition_grantees + total_no_of_sif_grantees + total_no_of_crmif_grantees

        grantee_wise_installment_dict['total_sef'] += total_no_of_grantee_sef
        grantee_wise_installment_dict['total_nutrition'] += total_no_of_nutrition_grantees
        grantee_wise_installment_dict['total_sif'] += total_no_of_sif_grantees
        grantee_wise_installment_dict['total_crmif'] += total_no_of_crmif_grantees
        grantee_wise_installment_dict['total_grantee'] += total_grantee

        row = [city_name, ward_name,ward_poverty_index, total_no_of_grantee_sef, total_no_of_nutrition_grantees, total_no_of_sif_grantees, total_no_of_crmif_grantees, total_grantee]

        response_data.append(row)

    footer_row = ['Total (all cities)','','']
    for grant_value in grantee_wise_installment_dict.values():
        grantee_percentage = grant_value / total_grantee * 100 if total_grantee else 0
        footer_row.append('{0}'.format(thousand_separator(int(grant_value))))
        # footer_row.append('{0:.0f}% ({1})'.format(grantee_percentage, thousand_separator(int(grant_value))))
    response_data.append(footer_row)
    return response_data

def get_grantees_by_ward_prioritization_index_chart_data(towns=list):
    print(towns)
    wards = dict()
    wards = Geography.objects.filter(type='Ward')

    grantee_wise_installment_dict = OrderedDict()
    grantee_wise_installment_dict['Total SEF'] = 0
    grantee_wise_installment_dict['Total Nutrition'] = 0
    grantee_wise_installment_dict['Total SIF'] = 0
    grantee_wise_installment_dict['Total CRMIF'] = 0
    
    for ward in wards:
        
        ward_name= ward.name
        ward_id= ward.id

        # City Name
        city = Geography.objects.filter(id=ward.parent_id)
        city_id = city[0].id
        city_name = city[0].name
        
        ## No Of grantees SEF
        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).exclude(ward=None).values('city_id', 'ward')
        ng = queryset.filter(city_id=city_id, ward=ward_name)\
            .annotate(Sum('no_of_business_grantee'),
                      Sum('no_of_apprenticeship_grantee'),
                      Sum('no_of_education_dropout_grantee'),
                      Sum('no_education_early_marriage_grantee'),
                      Sum('no_of_nutrition_grantees')
            )
        # No of nutrition grantees
        nTotal = 0
        total = 0
        for n in ng:
            if n['ward']:
                nTotal = n['no_of_nutrition_grantees__sum']
                if n['no_of_business_grantee__sum']:
                    total += n['no_of_business_grantee__sum']
                if n['no_of_apprenticeship_grantee__sum']:
                    total += n['no_of_apprenticeship_grantee__sum']
                if n['no_of_education_dropout_grantee__sum']:
                    total += n['no_of_education_dropout_grantee__sum']
                if n['no_education_early_marriage_grantee__sum']:
                    total += n['no_education_early_marriage_grantee__sum']
        total_no_of_grantee_sef = total

        total_no_of_nutrition_grantees = nTotal


        ## No Of grantees SIF
        queryset = Intervention.objects.filter(
            sif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.SIF'
        ).distinct().values(
            'sif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
       
        tSIF = 0
        for q in queryset:
            if q['number_of_total_pg_member_beneficiary__sum']:
                tSIF = q['number_of_total_pg_member_beneficiary__sum']
            if q['number_of_total_non_pg_member_beneficiary__sum']:
                tSIF += q['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_sif_grantees = tSIF
     
        ## No Of grantees CRMIF
        queryset = Intervention.objects.filter(
            crmif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.CRMIF'
        ).distinct().values(
            'crmif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
        # print(queryset)
        tCRMIF = 0
        if queryset.count()>0:
            if queryset[0]['number_of_total_pg_member_beneficiary__sum']:
                tCRMIF = queryset[0]['number_of_total_pg_member_beneficiary__sum']
            if queryset[0]['number_of_total_non_pg_member_beneficiary__sum']:
                tCRMIF += queryset[0]['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_crmif_grantees = tCRMIF

        grantee_wise_installment_dict['Total SEF'] += total_no_of_grantee_sef
        grantee_wise_installment_dict['Total Nutrition'] += total_no_of_nutrition_grantees
        grantee_wise_installment_dict['Total SIF'] += total_no_of_sif_grantees
        grantee_wise_installment_dict['Total CRMIF'] += total_no_of_crmif_grantees

    data = [
        {
            'name': 'Value of grants distributed',
            'data': list(grantee_wise_installment_dict.values())
        }
    ]

    return data, list(
        map(lambda grant_name: grant_name.replace('Grantees', ''), grantee_wise_installment_dict.keys()))

def get_grantees_by_ward_prioritization_index_table_data_old(towns=list):
    # SEFGranteesInfoCache.objects.all().delete()
    # SEFGranteesInfoCache.generate_sef_grantees_info_cache()
    print('Entered......')
    ng = SEFGranteesInfoCache.objects.annotate(Sum('no_of_business_grantee'),
                      Sum('no_of_apprenticeship_grantee'),
                      Sum('no_of_education_dropout_grantee'),
                      Sum('no_education_early_marriage_grantee'),
                      Sum('no_of_nutrition_grantees')
        )
    nTotal = 0
    total = 0
    no_of_business_grantee = 0
    no_of_apprenticeship_grantee = 0
    no_of_education_dropout_grantee = 0
    no_education_early_marriage_grantee = 0
    print('total_no_of_grantee_sef : '+total_no_of_grantee_sef)    
    print('total_no_of_nutrition_grantees : '+total_no_of_nutrition_grantees)    
    print('no_of_apprenticeship_grantee : '+no_of_apprenticeship_grantee)    
    print('no_of_education_dropout_grantee : '+no_of_education_dropout_grantee)    
    print('no_education_early_marriage_grantee : '+no_education_early_marriage_grantee)    
    print('no_of_business_grantee : '+no_of_business_grantee) 
    print(ng)
    for n in ng:
        nTotal += n['no_of_nutrition_grantees__sum']
        if n['no_of_business_grantee__sum']:
            total += n['no_of_business_grantee__sum']
            no_of_business_grantee += n['no_of_business_grantee__sum']
        if n['no_of_apprenticeship_grantee__sum']:
            total += n['no_of_apprenticeship_grantee__sum']
            no_of_apprenticeship_grantee += n['no_of_apprenticeship_grantee__sum']
        if n['no_of_education_dropout_grantee__sum']:
            total += n['no_of_education_dropout_grantee__sum']
            no_of_education_dropout_grantee += n['no_of_education_dropout_grantee__sum']
        if n['no_education_early_marriage_grantee__sum']:
            total += n['no_education_early_marriage_grantee__sum']
            no_education_early_marriage_grantee += n['no_education_early_marriage_grantee__sum']
    total_no_of_grantee_sef = total

    total_no_of_nutrition_grantees = nTotal
    print('total_no_of_grantee_sef : '+total_no_of_grantee_sef)    
    print('total_no_of_nutrition_grantees : '+total_no_of_nutrition_grantees)    
    print('no_of_apprenticeship_grantee : '+no_of_apprenticeship_grantee)    
    print('no_of_education_dropout_grantee : '+no_of_education_dropout_grantee)    
    print('no_education_early_marriage_grantee : '+no_education_early_marriage_grantee)    
    print('no_of_business_grantee : '+no_of_business_grantee)    
    return
    from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.grantees_by_wpi import GranteesByWPI
    GranteesByWPI.objects.all().delete()
    wards = dict()
    wards = Geography.objects.filter(type='Ward')

    response_data = []
    header_row = ['City Corporation/Pourosova', 'Ward No', 'Ward Poverty Index', 'Ward Wise Population', 'Ward Wise Registration', 'Average-MPI', 
    'No. of Total Grantee-SEF', 'No. of Total Grantee-Nutrition', 'No. of Grantee-SIF', 'No. of Grantee-CRMIF',
    'Total Grantee', 'Total Family Member Benefited']
   

    response_data.append(header_row)

    
    for ward in wards:
        
        # print(city[0].name)
        if not ward:
            continue
        # Ward Name
        ward_name= ward.name
        ward_id= ward.id

        # City Name
        city = Geography.objects.filter(id=ward.parent_id)
        if(city):
            city_id = city[0].id
            city_name = city[0].name
        else:
           continue
        # Ward Poverty Index(WPI)
        query = WordPrioritizationIndicator.objects.filter(Ward_id=ward_id).values('poverty_index_quantile', 'total_population')


        totPop = 0
        wpi = ""
        # if query.count()>0:
        #     wpi = "Q"+str(query[0])
        #     if query['total_population']:
        #         totPop = query['total_population']
        # else:
        #     wpi = ""
        #     totPop = 0
        for b in query:
            if b['poverty_index_quantile']:
                wpi = "Q"+str(b['poverty_index_quantile'])
            else:
                wpi = ""

            if b['total_population']:
                totPop = b['total_population']
            else:
                totPop = 0

        ward_poverty_index = wpi
        # Ward wise population
        # query = WordPrioritizationIndicator.objects.filter(Ward_id=ward_id).values('total_population')

        # totPop2 = 0
        # for l in query:
        #     if l['total_population']:
        #         totPop2 = l['total_population']
        # total_population2 = totPop2
        total_population = totPop

        # print("Tot Popu")
        # print(ward_poverty_index)
        # print(total_population)
        # print("Tot Popull")
        # print(total_population2)


        # Ward wise registration
        print(city_name)
        total_pg_registration = PGMemberInfoCache.objects.filter(ward_id=ward_id).aggregate(Sum('pg_count'))['pg_count__sum']
        print(city_name)
        print(ward_id)
        print(ward_name)
        if total_pg_registration is None:
            total_pg_registration = 0
        print(total_pg_registration)
        
        dquery = PGMemberInfoCache.objects.filter(ward_id=ward_id).values('ward_id','pg_count')\
            .annotate(
                total_members=Sum('household_member_count'),
                count=Sum('pg_count')
            )
        tFamilyMemBenefited = 0
        totReg = 0
        if dquery.count()>0:
            for k in dquery:
                if k['pg_count']:
                    totReg+=k['pg_count']
                total_member = k['total_members']
                total_hh = k['count']
                tFamilyMemBenefited =(total_member / total_hh)
            else:
                tFamilyMemBenefited = 0
        # total_pg_registration = totReg
        # print(total_pg_registration)
        # exit()
        
        # Ward average MPI(Divide total MPI over all pg menmber by total number of pg member)

        clients = Client.objects.filter(assigned_to__parent__address__geography_id=ward_id)\
            .values_list('id',flat=True)

        query = PGMPIIndicator.objects.filter(primary_group_member_id__in=clients)\
            .values('mpi_score')

        totalMpi = 0
        if query.count()>0:
            for j in query:
                if j['mpi_score']:
                    totalMpi += j['mpi_score']
        avgMpi = 0.00
        if total_pg_registration>0:
            avgMpi = totalMpi/total_pg_registration
        
        average_mpi_ward_wise = round(avgMpi, 2)
        
        ## No Of grantees SEF
        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False,is_deleted=False,is_version=False,is_active=True).exclude(ward=None).values('city_id', 'ward')
        ng = queryset.filter(city_id=city_id, ward=ward_name,is_deleted=False,is_version=False,is_active=True)\
            .annotate(Sum('no_of_business_grantee'),
                      Sum('no_of_apprenticeship_grantee'),
                      Sum('no_of_education_dropout_grantee'),
                      Sum('no_education_early_marriage_grantee'),
                      Sum('no_of_nutrition_grantees')
            )
        # No of nutrition grantees
        nTotal = 0
        total = 0
        for n in ng:
            if n['ward']:
                nTotal += n['no_of_nutrition_grantees__sum']
                if n['no_of_business_grantee__sum']:
                    total += n['no_of_business_grantee__sum']
                if n['no_of_apprenticeship_grantee__sum']:
                    total += n['no_of_apprenticeship_grantee__sum']
                if n['no_of_education_dropout_grantee__sum']:
                    total += n['no_of_education_dropout_grantee__sum']
                if n['no_education_early_marriage_grantee__sum']:
                    total += n['no_education_early_marriage_grantee__sum']
        total_no_of_grantee_sef = total

        total_no_of_nutrition_grantees = nTotal
        

        ## No Of grantees SIF
        queryset = Intervention.objects.filter(
            sif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.SIF'
        ).distinct().values(
            'sif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
       
        tSIF = 0
        for q in queryset:
            if q['number_of_total_pg_member_beneficiary__sum']:
                tSIF += q['number_of_total_pg_member_beneficiary__sum']
            if q['number_of_total_non_pg_member_beneficiary__sum']:
                tSIF += q['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_sif_grantees = tSIF
        
        ## No Of grantees CRMIF
        queryset = Intervention.objects.filter(
            crmif__assigned_cdc__address__geography_id=ward_id
        ).select_related('approvals.CRMIF'
        ).distinct().values(
            'crmif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )

        tCRMIF = 0
        if queryset.count()>0:
            if queryset[0]['number_of_total_pg_member_beneficiary__sum']:
                tCRMIF += queryset[0]['number_of_total_pg_member_beneficiary__sum']
            if queryset[0]['number_of_total_non_pg_member_beneficiary__sum']:
                tCRMIF += queryset[0]['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_crmif_grantees = tCRMIF
        
        ## Total grantee
        total_grantee = total_no_of_grantee_sef + total_no_of_nutrition_grantees + total_no_of_sif_grantees + total_no_of_crmif_grantees

        ## Toatl Family Member Benefited
        query = PGMemberInfoCache.objects.filter(city_id=city_id).values(
        'city__name')\
            .annotate(
                total_members=Sum('household_member_count'),
                count=Sum('pg_count')
            )
        
        tFamilyMemBenefited = 0
        if query.count()>0:
            for i in query:
                total_member = i['total_members']
                total_hh = i['count']
            tFamilyMemBenefited =(total_member / total_hh)
            
        else:
            tFamilyMemBenefited = 0

        total_family_member_benefited = math.ceil(tFamilyMemBenefited * (total_no_of_grantee_sef + total_no_of_nutrition_grantees))+total_no_of_sif_grantees + total_no_of_crmif_grantees
        
        # print("Total Family Member Benefited")
        # print(total_family_member_benefited)

        row = [city_name, ward_name, ward_poverty_index, total_population, total_pg_registration, average_mpi_ward_wise, total_no_of_grantee_sef, total_no_of_nutrition_grantees, total_no_of_sif_grantees, total_no_of_crmif_grantees, total_grantee, total_family_member_benefited]
        response_data.append(row)
        
        wpi_details=GranteesByWPI(city= city_name,ward = ward_name,city_id=city_id,ward_poverty_index=ward_poverty_index,
        total_population = total_population,total_pg_registration =total_pg_registration,average_mpi_ward_wise=average_mpi_ward_wise,
        sef_grantees = total_no_of_grantee_sef,nutrition_grantees=total_no_of_nutrition_grantees,sif_grantees=total_no_of_sif_grantees,
        crmif_grantees = total_no_of_crmif_grantees,total_grantee=total_grantee,total_grantee_int=total_grantee,total_family_member_benefited=total_family_member_benefited,total_family_member_benefited_int=total_family_member_benefited
        )
        wpi_details.save()
    return response_data    


