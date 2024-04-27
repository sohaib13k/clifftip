from django.urls import path
from . import views

urlpatterns = [
    path("", views.utilities, name="utilities-home"),
    path("excel-viewer/", views.excel_viewer, name="utilities-excel-viewer"),
]
