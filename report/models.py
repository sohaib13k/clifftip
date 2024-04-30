from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


class Report(models.Model):
    name = models.CharField(max_length=127, unique=True)
    service_name = models.CharField(
        max_length=127,
        unique=True,
        editable=False,
        help_text="Name of this models service method",
    )
    is_masterdata = models.BooleanField(default=False, verbose_name="Master data sheet")
    is_datetime_merged = models.BooleanField(default=False, verbose_name="Same column for date & time")
    date_col = models.CharField(max_length=127, null=True, blank=True, verbose_name="Date column header")
    time_col = models.CharField(max_length=127, null=True, blank=True, verbose_name="Time column header")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_tmstmp = models.DateTimeField(auto_now=True)
    access_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="accessible_reports_users", blank=True
    )
    access_groups = models.ManyToManyField(
        Group, related_name="accessible_reports_groups", blank=True
    )

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "reports"

    def save(self, *args, **kwargs):
        # Remove all spaces and convert to lowercase, this
        self.service_name = "_".join(self.name.split()).lower()
        super(Report, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
