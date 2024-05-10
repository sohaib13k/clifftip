# Generated by Django 5.0.4 on 2024-05-10 13:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_rename_last_updated_tmstmp_report_model_last_updated_tmstmp_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='data_source',
            field=models.CharField(choices=[('EXCEL', 'Excel Upload'), ('FORM', 'Form'), ('CUSTOM', 'Custom Report')], default='EXCEL', max_length=127),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='report_last_updated_tmstmp',
            field=models.DateTimeField(editable=False, null=True, verbose_name='report last uploaded'),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_company_id', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=127)),
                ('last_name', models.CharField(blank=True, max_length=127, null=True)),
                ('position', models.CharField(choices=[('Manager', 'Manager'), ('Engineer', 'Engineer'), ('Analyst', 'Analyst'), ('Assistant', 'Assistant'), ('Director', 'Director'), ('Sales', 'Sales Person')], max_length=127)),
                ('department', models.CharField(choices=[('HR', 'Human Resources'), ('IT', 'Information Technology'), ('FIN', 'Finance'), ('OPS', 'Operations'), ('SL', 'Sales')], max_length=127)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('phone_number', models.CharField(blank=True, max_length=127, null=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('manager_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees_managed', to='report.employee')),
                ('supervisor_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees_supervised', to='report.employee')),
            ],
            options={
                'verbose_name': 'employee',
                'verbose_name_plural': 'employees',
            },
        ),
    ]
