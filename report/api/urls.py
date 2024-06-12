from django.urls import path
from .views import view_filtered_excel

urlpatterns = [
    path("datefilter/excel/<int:report_id>/", view_filtered_excel, name="report-datefilter-excel-api"),
]
