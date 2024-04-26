from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import pandas as pd
from django.contrib.auth.decorators import login_required

@login_required
def utilities(request):
    return render(request, "utilities/utilities.html")

@login_required
def report(request):
    return render(request, "utilities/filter_report.html")

@login_required
def upload(request):
    return render(request, "utilities/upload_report.html")

@login_required
def handle_uploaded_file(f, relative_location):
    """
        saves file as the location

        # relative_location : this is with relative to base directory
    """
    rawdata_file_dir = settings.BASE_DIR / relative_location
    with open(rawdata_file_dir / f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def submit(request):
    if request.method == "POST" and request.FILES["excel_file"]:
        excel_file = request.FILES["excel_file"]
        if excel_file.name.endswith((".xls", ".xlsx")):
            try:
                handle_uploaded_file(excel_file, "reports")
                return HttpResponse("File uploaded successfully and saved!")
            except Exception as e:
                return HttpResponse("Error saving Excel file: " + str(e))
        else:
            return HttpResponse("Invalid file format. Please upload an Excel file.")
    return render(request, "upload_excel.html")
