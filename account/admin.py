from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, Clifftip, SailingClubSociety
from django.contrib.auth.models import Group


# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "profile"
    readonly_fields = ("used_storage",)


# Clifftip
class ClifftipUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # def get_queryset(self, request):
    #     # queryset = super().get_queryset(request)
    #     # return Clifftip.objects.all()
    #     pass

class ClifftipAdminSite(AdminSite):
    site_header = "Clifftip Admin"
    site_title = "Clifftip"

clifftip_admin_site = ClifftipAdminSite(name="clifftip")
clifftip_admin_site.register(Clifftip, ClifftipUserAdmin)
# clifftip_admin_site.register(Group)


# Sailing
class SailingClubSocietyUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # def get_queryset(self, request):
    #     # queryset = super().get_queryset(request)
    #     return SailingClubSociety.objects.all()

class SailingClubSocietyAdminSite(AdminSite):
    site_header = "Sailing Club Society Admin"
    site_title = "Sailing Club Society"

sailing_club_society_admin_site = SailingClubSocietyAdminSite(name="sailing_club_society")
sailing_club_society_admin_site.register(SailingClubSociety, SailingClubSocietyUserAdmin)
# sailing_club_society_admin_site.register(Group)