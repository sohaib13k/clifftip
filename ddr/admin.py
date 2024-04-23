from django.contrib import admin
from .models import CustomReport


@admin.register(CustomReport)
class CustomReportAdmin(admin.ModelAdmin):
    pass
