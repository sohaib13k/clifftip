from django.shortcuts import render

def utilities(request):
    return render(request, 'utilities/utilities.html')

def report(request):
    return render(request, 'utilities/filter_report.html')