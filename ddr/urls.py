from django.urls import path
from . import views

urlpatterns = [
    path("", views.ddr, name="ddr-home"),
    path("view/<int:report_id>/", views.view_report, name="ddr-view"),
]
