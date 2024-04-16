from django.urls import path
from . import views

urlpatterns = [
    path('', views.utilities, name='utilities-home'),
    path('report/', views.report, name='utilities-report'),
]
