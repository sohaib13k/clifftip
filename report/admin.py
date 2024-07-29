from django.contrib import admin
from .models import Report, Employee, DBBackup, PendingSalesOrderControl, FreightChargesMaster
from .forms import ReportForm
from django.shortcuts import render, redirect
from account.admin import sailing_club_society_admin_site, clifftip_admin_site
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.shortcuts import render
from .forms import UserSelectionForm
from account.models import Clifftip, SailingClubSociety

@admin.action(description="Give user access to selected report")
def give_report_useraccess(modeladmin, request, queryset):
    if "apply" in request.POST:
        form = UserSelectionForm(request.POST, admin_user=request.user)
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
        form = UserSelectionForm(admin_user=request.user)

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
        form = UserSelectionForm(request.POST, admin_user=request.user)
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
        form = UserSelectionForm(admin_user=request.user)

    context = {
        "form": form,
        "queryset": queryset,
        "opts": modeladmin.model._meta,
        "app_label": modeladmin.model._meta.app_label,
        "action": "remove",
    }

    return render(request, "admin/assign_user_to_access_report.html", context)


class ClifftipReportAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(company=Report.Company.CLIFFTIP)
    
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

    # list_filter = ["access_users", "access_groups"]

    readonly_fields = ("created_by", "report_last_updated_tmstmp")

    exclude = ["is_datetime_merged", "company"]

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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "access_users":
            kwargs["queryset"] = Clifftip.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def view_on_site(self, obj):
        pass

    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SailingClubSocietyReportAdmin(admin.ModelAdmin):

    # TODO: check if this method needed. Similar ones present in other places
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(company=Report.Company.SAILING_CLUB_SOCIETY)
    
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

    # list_filter = ["access_users", "access_groups"]

    readonly_fields = ("created_by", "report_last_updated_tmstmp")

    exclude = ["is_datetime_merged", "company"]

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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "access_users":
            kwargs["queryset"] = SailingClubSociety.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def view_on_site(self, obj):
        pass

    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


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


class FreightChargesMasterAdmin(admin.ModelAdmin):
    pass

clifftip_admin_site.register(Report, ClifftipReportAdmin)
sailing_club_society_admin_site.register(Report, SailingClubSocietyReportAdmin)
clifftip_admin_site.register(Employee, EmployeeAdmin)
# clifftip_admin_site.register(DBBackup, DBBackupAdmin)
clifftip_admin_site.register(PendingSalesOrderControl, PendingSalesOrderControlAdmin)
clifftip_admin_site.register(FreightChargesMaster, FreightChargesMasterAdmin)
