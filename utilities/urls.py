from django.urls import path
from . import views

urlpatterns = [
    path('', views.utilities, name='utilities-home'),
    path('report/', views.report, name='utilities-report'),
    path('report/upload/', views.upload, name='utilities-report-upload'),
    path('report/submit/', views.submit, name='utilities-report-submit'),

]
