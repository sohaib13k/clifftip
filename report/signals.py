from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report
from django.db import transaction


@receiver(post_save, sender=Report, dispatch_uid="570db2c4-59ea-4533-b65f-e2c02fec1454")
def course_access_to_superuser(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: add_superusers_to_report(instance))


def add_superusers_to_report(report):
    superusers = User.objects.filter(is_superuser=True)
    report.access_users.add(*superusers)


# TODO: add a button on report view UI for new superusers, that adds all report in their view