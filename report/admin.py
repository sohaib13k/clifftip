from django.contrib import admin
from .models import Report
from .forms import ReportForm


class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    list_display = [
        "name",
        "is_custom_report",
        "is_masterdata",
        "date_col",
        "last_updated_tmstmp",
    ]
    filter_horizontal = ["access_users", "access_groups", "reports"]

    search_fields = ["name"]

    readonly_fields = ("created_by", "created_date", "service_name")

    def view_on_site(self, obj):
        pass


admin.site.register(Report, ReportAdmin)
