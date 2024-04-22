from django.db import models


class CustomReport(models.Model):
    name = models.CharField(max_length=127, 



    class Meta:
        verbose_name = _("customreport")
        verbose_name_plural = _("customreports")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("customreport_detail", kwargs={"pk": self.pk})
