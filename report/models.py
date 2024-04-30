from django.db import models


class Report(models.Model):
    name = models.CharField(max_length=127, unique=True)
    is_masterdata = models.BooleanField(default=False)
    is_datetime_merged = models.BooleanField(default=False, null=True, blank=True)
    date_col = models.CharField(max_length=127, null=True, blank=True)
    time_col = models.CharField(max_length=127, null=True, blank=True)
    created_by = models.CharField(max_length=127)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_tmstmp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "reports"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
