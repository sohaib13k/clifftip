from django.urls import path, include
from . import views

urlpatterns = [
    # path('', views.index, name='home-index'),
    path('', include('account.urls')),
]
