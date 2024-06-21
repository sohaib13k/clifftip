from django.urls import path
from .views import view_filtered_excel, view_filtered_data

urlpatterns = [
    path("datefilter/excel/<int:report_id>/", view_filtered_excel, name="report-datefilter-excel-api"),
    path("datefilter/data/<int:report_id>/", view_filtered_data, name="report-datefilter-data-api"),
]
