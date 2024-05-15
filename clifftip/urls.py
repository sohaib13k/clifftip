"""
URL configuration for clifftip project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from account.views import change_color_theme, profile

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ddr.urls")),
    path("ddr/", include("ddr.urls")),
    path("utilities/", include("utilities.urls")),
    path("account/", include("account.urls")),
    path("report/", include("report.urls")),
]

# api routes for report
urlpatterns += [path("api/report/", include("report.api.urls"))]

# route for profile views
urlpatterns += [
    path("profile/theme/", change_color_theme, name="change_color_theme"),
    path("profile/", profile, name="profile")
]