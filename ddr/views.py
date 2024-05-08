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
    report = Report.objects.get(service_name="all_parties")
    latest_file = commonutil.get_latest_csv_from_dir(report)

    columns_to_read = ["Company Name", "Sales Person", "GST No.", "Mobile"]

    df = pd.DataFrame()
    counts = {}

    if latest_file is not None:
        # df = pd.read_csv(latest_file)
        df = pd.read_csv(latest_file, usecols=columns_to_read)
        
        total_entries = len(df)-1  # Total number of entries in the DataFrame

        for column in df.columns:
            column_count = df[column].count()  # Count of non-null values in the column
            difference = total_entries - column_count  # Difference from total entries
            counts[column] =  difference if difference>=0 else 0

    return render(request, "ddr/ddr.html", {"result": counts})