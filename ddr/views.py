from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import pandas as pd
import json
from django.contrib.auth.decorators import login_required


@login_required
def ddr(request):
    return render(request, "ddr/ddr.html")
