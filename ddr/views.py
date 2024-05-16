from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import pandas as pd
import json
from commonutil import commonutil
from django.contrib.auth.decorators import login_required
from report.models import Report
from account.models import UserProfile
from .models import AllPartiesSelectedColumns, AllPartiesThreshold


@login_required
def ddr(request):
    csv_all_parties_with_sale = commonutil.get_latest_csv_from_dir(
        Report.objects.get(service_name="all_parties_with_sale")
    )

    report = Report.objects.get(service_name="all_parties_with_sale")

    # columns_to_read = ["Company Name", "Sales Person", "GST No.", "Mobile"]

    df_all_parties = pd.DataFrame()
    counts = {}

    selected_columns_record = AllPartiesSelectedColumns.objects.filter(
        user=request.user
    ).first()
    selected_columns = (
        json.loads(selected_columns_record.columns) if selected_columns_record else []
    )

    all_parties_thresholds = AllPartiesThreshold.objects.first()
    thresholds = all_parties_thresholds.__dict__ if all_parties_thresholds else {}

    if csv_all_parties_with_sale is not None:
        df_all_parties = pd.read_csv(csv_all_parties_with_sale)

        total_entries = (
            len(df_all_parties) - 1
        )  # Total number of entries in the DataFrame

        for column in df_all_parties.columns:
            column_count = df_all_parties[
                column
            ].count()  # Count of non-null values in the column
            difference = total_entries - column_count  # Difference from total entries
            counts[column] = difference if difference >= 0 else 0

    return render(
        request,
        "ddr/ddr.html",
        {
            "result": counts,
            "report": report,
            "selected_columns": selected_columns,
            "threshold": thresholds,
            "theme": UserProfile.objects.get(user=request.user).color_theme,
        },
    )
