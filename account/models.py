from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    AVAILABLE_THEME = (
        ("light", "Light"),
        ("dark", "Dark"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    used_storage = models.IntegerField(default=0, editable=False)  # Used storage in MB
    storage_limit = models.IntegerField(default=100, verbose_name="storage limit (MB)")  # Storage limit in MB, default 100MB
    color_theme = models.CharField(max_length=127, null=True, blank=True, choices=AVAILABLE_THEME, default="light")

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to create/update user profile automatically when a user is created/updated
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
