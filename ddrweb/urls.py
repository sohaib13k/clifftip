from django.urls import path
from . import views

urlpatterns = [
    path('', views.ddrweb, name='ddrweb-home'),
    path('viewReport/<slug:fileName>/', views.viewReport, name='ddrweb-viewReport'),
]
