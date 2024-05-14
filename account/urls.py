from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path("", user_login, name="account-login"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", user_register, name="register"),
]

# profile URLs present in root urls.py 