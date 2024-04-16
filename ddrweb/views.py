from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import os
from django.conf import settings

def ddrweb(request):
    directory_path = os.path.join(settings.BASE_DIR , 'reports')
    
    reports = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    return render(request, 'ddrweb/ddrweb.html', {'reports':reports})

def viewReport(request, fileName):
    filename = '../reports/'+str(fileName)
    df = pd.read_excel(filename, header=2, index_col=0)

    try:
        value = df.at['Total', 'Amount']
        return render(request, 'ddrweb/viewReport.html', df)
    except KeyError as e:
        print(f"Key error: {e} - Check if the specified row or column exists.")
