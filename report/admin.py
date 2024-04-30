from django.contrib import admin
from .models import Report
from .forms import ReportForm


class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    list_display = [
        "name",
        "is_masterdata",
        "date_col",
        "time_col",
        "is_datetime_merged",
        "last_updated_tmstmp",
    ]
    filter_horizontal = ["access_users", "access_groups"]

    search_fields = ["name"]

    def view_on_site(self, obj):
        pass


admin.site.register(Report, ReportAdmin)
