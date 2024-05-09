from django.urls import path
from .views import view_filtered_report

urlpatterns = [
    path("<int:report_id>/", view_filtered_report, name="report-api"),
]
