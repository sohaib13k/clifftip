from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import pandas as pd
import json
from commonutil import commonutil
from django.contrib.auth.decorators import login_required
from report.models import Report


@login_required
def ddr(request):
    report = Report.objects.get(id=4)
    latest_file = commonutil.get_latest_csv_from_dir(report)

    columns_to_read = ["Company Name", "GST No.", "Mobile", "Sales Person"]

    df = pd.DataFrame()
    if latest_file is not None:
        df = pd.read_csv(latest_file, usecols=columns_to_read)

    columns = df.columns
    entry_counts = df.count()
    unique_counts = df.nunique()

    result = {}
    for column in columns:
        result[column] = {
            "number_of_entries": entry_counts[column],
            "number_of_unique_entries": unique_counts[column],
        }

    return render(request, "ddr/ddr.html", {"result": result})
