# models.py

from django.db import models
from django.conf import settings


class AllPartiesSelectedColumns(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    columns = models.TextField()  # Store as JSON

    def __str__(self):
        return f"{self.user.username}'s selected columns"


class AllPartiesThreshold(models.Model):
    danger = models.IntegerField(default=0)
    action = models.IntegerField(default=0)
    acceptable = models.IntegerField(default=0)


class BomReportOldDataVisibility(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    count = models.IntegerField(default=7)


class RoutingReportOldDataVisibility(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    count = models.IntegerField(default=7)
