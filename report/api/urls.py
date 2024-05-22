from django.urls import path
from .views import view_filtered_report

urlpatterns = [
    path("datefilter/<int:report_id>/", view_filtered_report, name="report-datefilter-api"),
]
