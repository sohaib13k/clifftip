from django.db import models


class Report(models.Model):

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "reports"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
