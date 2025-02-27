# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2022-01-31 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nuprp_admin', '0001_initial'),
        ('approvals', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CumulativeReportField',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.customfield',),
        ),
        migrations.CreateModel(
            name='MonthlyReportField',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.customfield',),
        ),
        migrations.AddField(
            model_name='waterintervention',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='waterintervention',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='waterintervention',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='waterintervention',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.WaterIntervention'),
        ),
        migrations.AddField(
            model_name='waterintervention',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Geography'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.ViolenceAgainstWomanCommittee'),
        ),
        migrations.AddField(
            model_name='violenceagainstwomancommittee',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='attachment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.FileObject'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.VAWGEFMReductionInitiative'),
        ),
        migrations.AddField(
            model_name='vawgefmreductioninitiative',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='activities_of_partnerships',
            field=models.ManyToManyField(to='approvals.ActivitiesOfPartnership'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='agreed_partnerships',
            field=models.ManyToManyField(to='approvals.AgreedPartnership'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='awareness_raising_by_sccs',
            field=models.ManyToManyField(to='approvals.AwarenessRaisingBySCC'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='cdc_cluster',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='nuprp_admin.CDCCluster'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Geography'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='explored_partnerships',
            field=models.ManyToManyField(to='approvals.ExploredPartnership'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='function_of_scc',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='approvals.FunctionOfSCC'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.VAWGEarlyMarriagePreventionReporting'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='safety_security_initiatives',
            field=models.ManyToManyField(to='approvals.SafetySecurityInitiative'),
        ),
        migrations.AddField(
            model_name='vawgearlymarriagepreventionreporting',
            name='vawg_and_efm_reduction_initiatives',
            field=models.ManyToManyField(to='approvals.VAWGEFMReductionInitiative'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Geography'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.TotalSaving'),
        ),
        migrations.AddField(
            model_name='totalsaving',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='sifinstallment',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='sifinstallment',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
        migrations.AddField(
            model_name='sifinstallment',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='sifinstallment',
            name='master_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='version_master', to='approvals.SIFInstallment'),
        ),
        migrations.AddField(
            model_name='sifinstallment',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization'),
        ),
        migrations.AddField(
            model_name='sifandcrmifintervention',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Geography'),
        ),
        migrations.AddField(
            model_name='sifandcrmifintervention',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.ConsoleUser'),
        ),
        migrations.AddField(
            model_name='sifandcrmifintervention',
            name='entity_meta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.DomainEntityMeta'),
        ),
    ]
