from django.urls import path
from . import views

urlpatterns = [
    path('', views.utilities, name='utilities-home'),
    path('filterReport/', views.filterReport, name='utilities-filterReport'),
]
