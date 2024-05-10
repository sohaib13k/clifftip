from django.contrib import admin
from .models import Report, Employee
from .forms import ReportForm


class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    list_display = [
        "name",
        "is_custom_report",
        "date_col",
        "report_last_updated_tmstmp",
    ]
    filter_horizontal = ["access_users", "access_groups", "reports"]

    search_fields = ["name"]

    list_filter = ['access_users', 'access_groups']

    readonly_fields = ("created_by", "report_last_updated_tmstmp")

    exclude = ["is_datetime_merged"]

    def view_on_site(self, obj):
        pass


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'department', 'position']
    search_fields = ['first_name', 'last_name', 'department', 'position', 'phone_number']
    list_filter = ['department', 'position']


admin.site.register(Report, ReportAdmin)
admin.site.register(Employee, EmployeeAdmin)