from django.urls import path
from .views import saveEntity


urlpatterns = [
    path("saveEntity/", saveEntity, name="ddr-api-saveEntity"),
]
