from django.contrib import admin
from .models import Report


class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_masterdata",
        "date_col",
        "time_col",
        "is_datetime_merged",
        "last_updated_tmstmp",
    ]
    filter_horizontal = ["access_users", "access_groups"]

    def view_on_site(self, obj):
        pass


admin.site.register(Report, ReportAdmin)
