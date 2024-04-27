from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from commonutil import commonutil
from django.http import HttpResponse


@login_required
def report(request):
    return render(request, "report/report.html")


@login_required
def upload(request):
    if request.method == "POST" and request.FILES["excel_file"]:
        excel_file = request.FILES["excel_file"]
        if excel_file.name.endswith((".xls", ".xlsx")):
            try:
                commonutil.uploaded_excel(excel_file, settings.REPORTS_DIR)
                return HttpResponse("File uploaded successfully and saved!")
            except Exception as e:
                return HttpResponse("Error saving Excel file: " + str(e))
        else:
            return HttpResponse("Invalid file format. Please upload an Excel file.")
    return render(request, "report/upload_report.html")


@login_required
def add(request):
    pass
