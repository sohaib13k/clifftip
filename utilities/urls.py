from django.urls import path
from . import views

urlpatterns = [
    path("", views.utilities, name="utilities-home"),
    path("excel-viewer/", views.excel_viewer, name="utilities-excel-viewer"),
]

# report related urls
report_pattern = [
    path("report-upload/", views.upload, name="utilities-report-upload"),
    path("report-submit/", views.submit, name="utilities-report-submit"),
]

urlpatterns += report_pattern