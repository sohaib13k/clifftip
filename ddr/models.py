# models.py

from django.db import models
from django.contrib.auth.models import User


class AllPartiesSelectedColumns(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    columns = models.TextField()  # Store as JSON

    def __str__(self):
        return f"{self.user.username}'s selected columns"


class AllPartiesThreshold(models.Model):
    danger = models.IntegerField(default=0)
    action = models.IntegerField(default=0)
    acceptable = models.IntegerField(default=0)


class BomReportOldDataVisibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=7)


class RoutingReportOldDataVisibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=7)
