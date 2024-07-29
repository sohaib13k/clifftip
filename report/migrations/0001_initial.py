# Generated by Django 5.0.4 on 2024-07-27 11:13

import django.db.models.deletion
import report.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DBBackup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("db_dump", models.FileField(upload_to=report.models.get_upload_to)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="FreightChargesMaster",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("party_name", models.CharField(max_length=127, unique=True)),
                ("charge_per_trip", models.CharField(max_length=127)),
            ],
        ),
        migrations.CreateModel(
            name="PendingSalesOrderControl",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reason", models.CharField(max_length=127, unique=True)),
                (
                    "Controllable",
                    models.CharField(
                        choices=[
                            ("Yes", "Yes"),
                            ("No", "No"),
                            ("Exceptional", "Exceptional"),
                        ],
                        max_length=127,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("employee_company_id", models.IntegerField(blank=True, null=True)),
                ("first_name", models.CharField(max_length=127)),
                ("last_name", models.CharField(blank=True, max_length=127, null=True)),
                (
                    "job_title",
                    models.CharField(
                        choices=[
                            ("SE", "Sales Executive"),
                            ("TC", "Tally caller"),
                            ("ADM", "Admin"),
                            ("MO", "Machine Operator"),
                            ("AMO", "Ast. Machine Opt."),
                            ("HEL", "Helper"),
                            ("FI", "Floor Incharge"),
                            ("GI", "Godown Incharge"),
                            ("OFC", "Office"),
                            ("ACC", "Accountant"),
                            ("MIS", "Misc."),
                            ("PC", "Production Cordinator"),
                            ("PUR", "Purchase"),
                            ("DI", "Dispatch Incharge"),
                            ("MI", "Maintainance Incharge"),
                            ("QI", "Quality Incharge"),
                            ("BI", "Billing Incharge"),
                            ("SC", "Sales Cordinator"),
                            ("LM", "Lead Manager"),
                        ],
                        max_length=127,
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        choices=[
                            ("PRD", "Production"),
                            ("DIS", "Dispatch"),
                            ("QA", "Quality"),
                            ("TLY", "Tally Calling"),
                            ("SL", "Sales"),
                            ("HR", "H.R"),
                            ("PR", "Purchase"),
                            ("CF", "C&F"),
                            ("ACC", "Accounts"),
                            ("GD", "Godown"),
                            ("NSD", "New Sales Division"),
                            ("ECD", "Existing Client Division"),
                            ("CSD", "Cross Sales Division"),
                            ("BIL", "Billing"),
                            ("MNT", "Maintenence"),
                            ("IT", "I.T"),
                        ],
                        max_length=127,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=127, null=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "manager_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="employees_managed",
                        to="report.employee",
                    ),
                ),
                (
                    "supervisor_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="employees_supervised",
                        to="report.employee",
                    ),
                ),
            ],
            options={
                "verbose_name": "employee",
                "verbose_name_plural": "employees",
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=127, unique=True)),
                (
                    "service_name",
                    models.CharField(
                        editable=False,
                        help_text="Name of this model service method",
                        max_length=127,
                        unique=True,
                    ),
                ),
                (
                    "is_masterdata",
                    models.BooleanField(
                        default=False, verbose_name="Master data sheet"
                    ),
                ),
                (
                    "is_datetime_merged",
                    models.BooleanField(
                        default=False, verbose_name="Same column for date & time"
                    ),
                ),
                (
                    "date_col",
                    models.CharField(
                        blank=True,
                        max_length=127,
                        null=True,
                        verbose_name="Date column header",
                    ),
                ),
                (
                    "time_col",
                    models.CharField(
                        blank=True,
                        max_length=127,
                        null=True,
                        verbose_name="Time column header",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("model_last_updated_tmstmp", models.DateTimeField(auto_now=True)),
                (
                    "report_last_updated_tmstmp",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="report last uploaded"
                    ),
                ),
                (
                    "is_custom_report",
                    models.BooleanField(
                        default=False, verbose_name="customised report"
                    ),
                ),
                (
                    "data_source",
                    models.CharField(
                        choices=[
                            ("EXCEL", "Excel Upload"),
                            ("FORM", "Form"),
                            ("CUSTOM", "Custom Report"),
                        ],
                        max_length=127,
                    ),
                ),
                (
                    "company",
                    models.TextField(
                        choices=[
                            ("CLIFFTIP", "Clifftip"),
                            ("SAILING_CLUB_SOCIETY", "Sailing Club Society"),
                        ],
                        max_length=127,
                    ),
                ),
                (
                    "access_groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="accessible_reports_groups",
                        to="auth.group",
                    ),
                ),
                (
                    "access_users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="accessible_reports_users",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reports",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_report_parents",
                        to="report.report",
                    ),
                ),
            ],
            options={
                "verbose_name": "report",
                "verbose_name_plural": "reports",
            },
        ),
    ]
