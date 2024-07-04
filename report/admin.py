from django.contrib import admin
from .models import Report, Employee, DBBackup, PendingSalesOrderControl
from .forms import ReportForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render
from .forms import UserSelectionForm


@admin.action(description="Give user access to selected report")
def give_report_useraccess(modeladmin, request, queryset):
    if "apply" in request.POST:
        form = UserSelectionForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data["user"]
            for obj in queryset:
                obj.access_users.add(selected_user)
                obj.save()

            modeladmin.message_user(
                request,
                f'User "{selected_user.username}" has been assigned {queryset.count()} report.',
            )
            return redirect(request.get_full_path())
    else:
        form = UserSelectionForm()

    context = {
        "form": form,
        "queryset": queryset,
        "opts": modeladmin.model._meta,
        "app_label": modeladmin.model._meta.app_label,
        "action": "give",
    }

    return render(request, "admin/assign_user_to_access_report.html", context)


@admin.action(description="Remove user access to selected report")
def remove_report_useraccess(modeladmin, request, queryset):
    if "apply" in request.POST:
        form = UserSelectionForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data["user"]
            for obj in queryset:
                obj.access_users.remove(selected_user)
                obj.save()

            modeladmin.message_user(
                request,
                f'User "{selected_user.username}" has been removed from accessing {queryset.count()} report.',
            )
            return redirect(request.get_full_path())
    else:
        form = UserSelectionForm()

    context = {
        "form": form,
        "queryset": queryset,
        "opts": modeladmin.model._meta,
        "app_label": modeladmin.model._meta.app_label,
        "action": "remove",
    }

    return render(request, "admin/assign_user_to_access_report.html", context)


class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    list_display = [
        "name",
        "is_custom_report",
        "date_col",
        "report_last_updated_tmstmp",
    ]

    actions = [give_report_useraccess, remove_report_useraccess]

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


class DBBackupAdmin(admin.ModelAdmin):
    pass


class PendingSalesOrderControlAdmin(admin.ModelAdmin):
    pass


admin.site.register(Report, ReportAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(DBBackup, DBBackupAdmin)
admin.site.register(PendingSalesOrderControl, PendingSalesOrderControlAdmin)
