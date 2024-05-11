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

    list_filter = ["access_users", "access_groups"]

    readonly_fields = ("created_by", "report_last_updated_tmstmp")

    exclude = ["is_datetime_merged"]

    fieldsets = [
        (
            "General Information",
            {
                "fields": (
                    "name",
                    "data_source",
                    "is_masterdata",
                    "date_col",
                    "time_col",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": ("access_users", "access_groups"),
                "classes": ("collapse",),  # Optional: Collapse the fieldset by default
            },
        ),
        (
            "System Information",
            {
                "fields": ("report_last_updated_tmstmp", "created_by"),
                "classes": ("collapse",),  # Optional: Collapse the fieldset by default
            },
        ),
        (
            "Custom Reports",
            {
                "fields": (
                    "is_custom_report",
                    "reports",
                ),
                "classes": ("collapse",),  # Optional: Collapse the fieldset by default
            },
        ),
    ]

    def view_on_site(self, obj):
        pass


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "department", "job_title"]

    search_fields = [
        "first_name",
        "last_name",
        "department",
        "job_title",
        "phone_number",
    ]

    list_filter = ["department", "job_title"]

    fieldsets = [
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "phone_number",
                ],
            },
        ),
        (
            "Employment Details",
            {
                "fields": ("employee_company_id", "job_title", "department"),
            },
        ),
        (
            "Hierarchy",
            {
                "fields": ("manager_id", "supervisor_id"),
                "classes": ("collapse",),  # Optional: Collapse the fieldset by default
            },
        ),
    ]


admin.site.register(Report, ReportAdmin)
admin.site.register(Employee, EmployeeAdmin)
