from django.urls import path
from . import views

urlpatterns = [
    path('', views.ddr, name='ddr-home'),
    path('view/<str:report>/', views.view_report, name='ddr-view'),
]
