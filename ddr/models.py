# models.py

from django.db import models
from django.contrib.auth.models import User


class SelectedColumns(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    columns = models.TextField()  # Store as JSON

    def __str__(self):
        return f"{self.user.username}'s selected columns"
