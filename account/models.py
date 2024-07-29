from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class User(AbstractUser):
    class Company(models.TextChoices):
        CLIFFTIP = "CLIFFTIP", "Clifftip"
        SAILING_CLUB_SOCIETY = "SAILING_CLUB_SOCIETY", "Sailing Club Society"

    company = models.TextField(max_length=127, null=False, blank=False, choices=Company.choices)


class ClifftipManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(company=User.Company.CLIFFTIP)

class Clifftip(User):
    objects = ClifftipManager()

    def save(self, *args, **kwargs):
        self.company = self.Company.CLIFFTIP
        super().save(*args, **kwargs)
        try:
            if self.profile:
                pass
        except:
            UserProfile.objects.create(user=self)

    class Meta:
        proxy = True


class SailingClubSocietyManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(company=User.Company.SAILING_CLUB_SOCIETY)

class SailingClubSociety(User):
    objects = SailingClubSocietyManager()


    def save(self, *args, **kwargs):
        self.company = self.Company.SAILING_CLUB_SOCIETY
        super().save(*args, **kwargs)
        try:
            if self.profile:
                pass
        except:
            UserProfile.objects.create(user=self)

    class Meta:
        proxy = True


class UserProfile(models.Model):
    AVAILABLE_THEME = (
        ("default", "Default"),
        ("dark", "Dark"),
        ("light", "Light"),
        ("colored", "Colored"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    used_storage = models.IntegerField(default=0, editable=False)  # Used storage in MB
    storage_limit = models.IntegerField(default=100, verbose_name="storage limit (MB)")  # Storage limit in MB, default 100MB
    color_theme = models.CharField(max_length=127, null=True, blank=True, choices=AVAILABLE_THEME, default="default")

    def __str__(self):
        return f"{self.user.username}'s Profile"