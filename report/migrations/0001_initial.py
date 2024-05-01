# Generated by Django 5.0.4 on 2024-05-01 00:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, unique=True)),
                ('service_name', models.CharField(editable=False, help_text='Name of this model service method', max_length=127, unique=True)),
                ('is_masterdata', models.BooleanField(default=False, verbose_name='Master data sheet')),
                ('is_datetime_merged', models.BooleanField(default=False, verbose_name='Same column for date & time')),
                ('date_col', models.CharField(blank=True, max_length=127, null=True, verbose_name='Date column header')),
                ('time_col', models.CharField(blank=True, max_length=127, null=True, verbose_name='Time column header')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated_tmstmp', models.DateTimeField(auto_now=True)),
                ('is_custom_report', models.BooleanField(default=False, verbose_name='customised report')),
                ('access_groups', models.ManyToManyField(blank=True, related_name='accessible_reports_groups', to='auth.group')),
                ('access_users', models.ManyToManyField(blank=True, related_name='accessible_reports_users', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('reports', models.ManyToManyField(blank=True, related_name='custom_report_parents', to='report.report')),
            ],
            options={
                'verbose_name': 'report',
                'verbose_name_plural': 'reports',
            },
        ),
    ]
