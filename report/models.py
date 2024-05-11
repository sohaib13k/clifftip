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
    is_datetime_merged = models.BooleanField(default=False, verbose_name="Same column for date & time")
    date_col = models.CharField(max_length=127, null=True, blank=True, verbose_name="Date column header")
    time_col = models.CharField(max_length=127, null=True, blank=True, verbose_name="Time column header")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )
    created_date = models.DateTimeField(auto_now_add=True)
    model_last_updated_tmstmp = models.DateTimeField(auto_now=True)
    report_last_updated_tmstmp = models.DateTimeField(null=True, editable=False, verbose_name="report last uploaded")
    access_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="accessible_reports_users", blank=True
    )
    access_groups = models.ManyToManyField(
        Group, related_name="accessible_reports_groups", blank=True
    )
    is_custom_report = models.BooleanField(default=False, verbose_name="customised report")
    reports = models.ManyToManyField(
        "self", related_name="custom_report_parents", symmetrical=False, blank=True
    )
    data_source = models.CharField(max_length=127, null=False, blank=False, choices=DATA_SOURCE_CHOICES)


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
    department = models.CharField(max_length=127, null=False, blank=False, choices=DEPARTMENT_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=127, null=True, blank=True)
    manager_id = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="employees_managed")
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
