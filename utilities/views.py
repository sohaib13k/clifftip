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


@login_required
def upload(request):
    return render(request, "utilities/upload_report.html")


@login_required
def submit(request):
    if request.method == "POST" and request.FILES["excel_file"]:
        excel_file = request.FILES["excel_file"]
        if excel_file.name.endswith((".xls", ".xlsx")):
            try:
                commonutil.uploaded_excel(
                    excel_file, settings.REPORTS_DIR
                )
                return HttpResponse("File uploaded successfully and saved!")
            except Exception as e:
                return HttpResponse("Error saving Excel file: " + str(e))
        else:
            return HttpResponse("Invalid file format. Please upload an Excel file.")
    return render(request, "upload_excel.html")
