from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.report, name="report-home"),
    path("upload/", views.upload, name="report-upload"),
    path("view/<int:report_id>/", views.view_report, name="report-view"),
]
