from django.shortcuts import render

def utilities(request):
    return render(request, 'utilities/utilities.html')

def filterReport(request):
    return render(request, 'utilities/filterReport.html')