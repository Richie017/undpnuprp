
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


__author__ = 'Ahsan@4Axiz'


def get_grantees_by_ward_prioritization_index_table_data(towns=list):


    wards = dict()
    wards = Geography.objects.filter(type='Ward')
    print('Print test')
    print(wards)

    response_data = []
    header_row = ['City Corporation/Pourosova', 'Ward No', 'Ward Poverty Index', 'Ward Wise Population', 'Ward Wise Registration', 'Average-MPI', 
    'No. of Total Grantee-SEF', 'No. of Total Grantee-Nutrition', 'No. of Grantee-SIF', 'No. of Grantee-CRMIF',
    'Total Grantee', 'Total Family Member Benefited']
   

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

        # Ward Poverty Index(WPI)
        query = WordPrioritizationIndicator.objects.filter(Ward_id=ward_id).values('poverty_index_quantile', 'total_population')

        print("Query")
        print(query)

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
        dquery = PGMemberInfoCache.objects.filter(ward_id=ward_id).values('ward_id','pg_count')\
            .annotate(
                total_members=Sum('household_member_count'),
                count=Sum('pg_count')
            )

        totReg = 0
        if dquery.count()>0:
            for k in dquery:
                totReg+=k['pg_count']

        total_pg_registration = totReg


        # Ward average MPI(Divide total MPI over all pg menmber by total number of pg member)

        # clients = Client.objects.filter(assigned_to__parent__address__geography_id=ward_id)\
        #     .values_list('id',flat=True)

        # query = PGMPIIndicator.objects.filter(primary_group_member_id__in=clients)\
        #     .values('mpi_score')

        # totalMpi = 0
        # if query.count()>0:
        #     for j in query:
        #         totalMpi += j['mpi_score']
        # avgMpi = 0.00
        # if total_pg_registration>0:
        #     avgMpi = totalMpi/total_pg_registration
        
        # average_mpi_ward_wise = round(avgMpi, 2)
        
        ## No Of grantees SEF
        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).exclude(ward=None).values('city_id', 'ward')
        ng = queryset.filter(city_id=city_id, ward=ward_name)\
            .annotate(Sum('no_of_business_grantee'),
                      Sum('no_of_apprenticeship_grantee'),
                      Sum('no_of_education_dropout_grantee'),
                      Sum('no_education_early_marriage_grantee'),
                      Sum('no_of_nutrition_grantees')
            )

        total = 0
        for n in ng:
            if n['ward']:
                total += n['no_of_business_grantee__sum']
                total += n['no_of_apprenticeship_grantee__sum']
                total += n['no_of_education_dropout_grantee__sum']
                total += n['no_education_early_marriage_grantee__sum']
        total_no_of_grantee_sef = total


        # No of nutrition grantees
        nTotal = 0
        for m in ng:
            if m['ward']:
                nTotal = m['no_of_nutrition_grantees__sum']
        total_no_of_nutrition_grantees = nTotal


        ## No Of grantees SIF
        queryset = Intervention.objects.filter(
            sif__assigned_cdc__address__geography__isnull=False
        ).select_related('approvals.SIF'
        ).distinct().values(
            'sif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )
       
        tSIF = 0
        for o in queryset:
            if o['sif__assigned_cdc__address__geography_id'] == ward_id:
                if o['sif__assigned_cdc__address__geography_id']:
                    tSIF = o['number_of_total_pg_member_beneficiary__sum']+o['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_sif_grantees = tSIF
     
        ## No Of grantees CRMIF
        queryset = Intervention.objects.filter(
            crmif__assigned_cdc__address__geography__isnull=False
        ).select_related('approvals.CRMIF'
        ).distinct().values(
            'crmif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_total_pg_member_beneficiary'),
                    Sum('number_of_total_non_pg_member_beneficiary')
        )

        tCRMIF = 0
        for p in queryset:
            if p['crmif__assigned_cdc__address__geography_id'] == ward_id:
                if p['crmif__assigned_cdc__address__geography_id']:
                    tCRMIF = p['number_of_total_pg_member_beneficiary__sum']+p['number_of_total_non_pg_member_beneficiary__sum']
        total_no_of_crmif_grantees = tCRMIF

        ## Total grantee
        total_grantee = total_no_of_grantee_sef + total_no_of_nutrition_grantees + total_no_of_sif_grantees + total_no_of_crmif_grantees

        ## Toatl Family Member Benefited
        # query = PGMemberInfoCache.objects.filter(city_id=city_id).values(
        # 'city__name')\
            # .annotate(
            #     total_members=Sum('household_member_count'),
            #     count=Sum('pg_count')
            # )
        
        tFamilyMemBenefited = 0
        if dquery.count()>0:
            for i in dquery:
                total_member = i['total_members']
                total_hh = i['count']
            tFamilyMemBenefited =(total_member / total_hh)
            
        else:
            tFamilyMemBenefited = 0

        total_family_member_benefited = math.ceil(tFamilyMemBenefited * total_grantee)
        
        # print("Total Family Member Benefited")
        # print(total_family_member_benefited)

        row = [city_name, ward_name, ward_poverty_index, total_population, total_pg_registration, "average_mpi_ward_wise", total_no_of_grantee_sef, total_no_of_nutrition_grantees, total_no_of_sif_grantees, total_no_of_crmif_grantees, total_grantee, total_family_member_benefited]

        response_data.append(row)

    return response_data


