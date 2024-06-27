import shutil
import zipfile
import os
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.utils.timezone import localtime, now
from time import localtime
from pathlib import Path
from django.utils.timezone import localtime
from django.db.models import Q
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import reverse


class Report(models.Model):
    DATA_SOURCE_CHOICES = (
        ("EXCEL", "Excel Upload"),
        ("FORM", "Form"),
        ("CUSTOM", "Custom Report"),
    )

    name = models.CharField(max_length=127, unique=True)
    service_name = models.CharField(
        max_length=127,
        unique=True,
        editable=False,
        help_text="Name of this model service method",
    )
    is_masterdata = models.BooleanField(default=False, verbose_name="Master data sheet")
    is_datetime_merged = models.BooleanField(
        default=False, verbose_name="Same column for date & time"
    )
    date_col = models.CharField(
        max_length=127, null=True, blank=True, verbose_name="Date column header"
    )
    time_col = models.CharField(
        max_length=127, null=True, blank=True, verbose_name="Time column header"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )
    created_date = models.DateTimeField(auto_now_add=True)
    model_last_updated_tmstmp = models.DateTimeField(auto_now=True)
    report_last_updated_tmstmp = models.DateTimeField(
        null=True, editable=False, verbose_name="report last uploaded"
    )
    access_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="accessible_reports_users", blank=True
    )
    access_groups = models.ManyToManyField(
        Group, related_name="accessible_reports_groups", blank=True
    )
    is_custom_report = models.BooleanField(
        default=False, verbose_name="customised report"
    )
    reports = models.ManyToManyField(
        "self", related_name="custom_report_parents", symmetrical=False, blank=True
    )
    data_source = models.CharField(
        max_length=127, null=False, blank=False, choices=DATA_SOURCE_CHOICES
    )

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "reports"

    def save(self, *args, **kwargs):
        # Remove all spaces and convert to lowercase, this
        if not self.service_name:
            self.service_name = "_".join(self.name.split()).lower()
        super(Report, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})

    @staticmethod
    def is_report_accessible(report_id, user):
        return (
            user.accessible_reports_users.filter(pk=report_id).exists()
            or Report.objects.filter(
                pk=report_id, access_groups__in=user.groups.all()
            ).exists()
        )

    @staticmethod
    def get_accessible_reportlist(user):
        return Report.objects.filter(
            Q(access_users=user) | Q(access_groups__in=user.groups.all())
        ).distinct()


class Employee(models.Model):
    DEPARTMENT_CHOICES = (
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
    )

    TITLE_CHOICES = (
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
    )

    employee_company_id = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=127, null=False)
    last_name = models.CharField(max_length=127, null=True, blank=True)
    job_title = models.CharField(max_length=127, choices=TITLE_CHOICES)
    department = models.CharField(
        max_length=127, null=False, blank=False, choices=DEPARTMENT_CHOICES
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )
    created_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=127, null=True, blank=True)
    manager_id = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_managed",
    )
    supervisor_id = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_supervised",
    )

    def __str__(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.first_name}"

    class Meta:
        verbose_name = "employee"
        verbose_name_plural = "employees"

    def get_absolute_url(self):
        return reverse("employee_detail", kwargs={"pk": self.pk})


def get_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    current_time = localtime(now())
    formatted_time = current_time.strftime("%d-%m-%Y_%H-%M-%S")
    filename = f"{formatted_time}.{ext}"
    return Path("temp") / filename


class DBBackup(models.Model):
    db_dump = models.FileField(upload_to=get_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_time = localtime(self.uploaded_at)
        return local_time.strftime("%d-%m-%Y %I:%M:%S %p")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        file_path = self.db_dump.path

        if file_path.endswith(".zip"):
            blob_name = Path(file_path).name
            extract_and_upload_to_azure(file_path, blob_name)


def extract_and_upload_to_azure(file_path, blob_name):
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        extracted_path = file_path.replace(".zip", "")
        zip_ref.extractall(extracted_path)

    blob_service_client = BlobServiceClient.from_connection_string(
        settings.AZURE_STORAGE_CONNECTION_STRING
    )
    container_client = blob_service_client.get_container_client(
        settings.AZURE_STORAGE_CONTAINER_NAME
    )

    for root, dirs, files in os.walk(extracted_path):
        for filename in files:
            file_path_on_blob = os.path.join(root, filename).replace(
                extracted_path, blob_name
            )
            blob_client = container_client.get_blob_client(file_path_on_blob)

            with open(os.path.join(root, filename), "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

    if os.path.exists(extracted_path):
        shutil.rmtree(extracted_path)

    temp_folder = Path(file_path).parent
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)


# class Parties(models.Model):
#     customer_name = models.CharField(max_length=127, unique=True)
#     gst_no = models.CharField(max_length=127, unique=True)
#     first_sale = models.DateField(null=True, blank=True)
#     last_sale = models.DateField(null=True, blank=True)
#     created_tmstmp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.customer_name

#     class Meta:
#         indexes = [
#             models.Index(fields=['customer_name']),
#             models.Index(fields=['gst_no']),
#             models.Index(fields=['customer_name', 'gst_no']),
#         ]
