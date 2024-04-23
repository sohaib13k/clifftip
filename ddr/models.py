from django.db import models
from django.urls import reverse


class CustomReport(models.Model):
    name = models.CharField(max_length=127)
    created_by = models.CharField(max_length=127)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_tmstmp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "custom report"
        verbose_name_plural = "custom reports"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("custom_report_detail", kwargs={"name": self.name})
