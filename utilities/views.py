from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from commonutil import commonutil
import pandas as pd


@login_required
def utilities(request):
    return render(request, "utilities/utilities.html")


@login_required
def excel_viewer(request):
    return render(request, "utilities/excel_viewer.html")
