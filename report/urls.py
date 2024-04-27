from django.urls import path
from . import views

urlpatterns = [
    path("", views.report, name="report-home"),
    path("upload/", views.upload, name="report-upload"),
    path("add/", views.add, name="report-add"),  # for adding new report metadata like- name, purpose, index_field
]
