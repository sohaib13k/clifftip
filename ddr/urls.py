from django.urls import path
from . import views

urlpatterns = [
    path("", views.ddr, name="ddr-home"),
]
