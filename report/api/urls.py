from django.urls import path
from .views import ReportView

urlpatterns = [
    path("<int:report_id>/", ReportView.as_view(), name="report-api"),
]
