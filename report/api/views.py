from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from report.models import Report
from django.conf import settings
from commonutil import commonutil
import os
import pandas as pd
from django.db.models import Q
from django.http import Http404
from . import report_logic

@login_required
def view_filtered_excel(request, report_id=None):
    report = Report.objects.filter(
        Q(access_users=request.user) | Q(access_groups__in=request.user.groups.all()),
        id=report_id,
    ).first()

    if not report:
        raise Http404("Invalid input provided.")

    if report.is_masterdata:
        return JsonResponse(
            {"error": "Masterdata cannot be filtered, since date column missing."},
            status=406,
        )

    interval = request.GET.get("interval")

    if interval:
        if interval not in ["day", "week", "month", "year"]:
            return JsonResponse({"error": "Invalid interval provided."}, status=400)
        start_date, end_date = commonutil.get_interval_date_str(interval)

    else:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not start_date or not end_date:
            return JsonResponse(
                {
                    "error": "Start date and end date required when interval is not provided."
                },
                status=400,
            )
    # start_date = "2024-05-01"
    start_year_month = tuple(map(int, start_date.split("-")[:2]))  # (year, month)
    end_year_month = tuple(map(int, end_date.split("-")[:2]))  # (year, month)

    csv_directory = settings.CSV_DIR / report.service_name

    agg_data = pd.DataFrame()

    try:
        for filename in os.listdir(csv_directory):
            if filename.endswith(".csv"):
                # Remove ".csv" extension
                file_year_month = tuple(map(int, filename[:-4].split("_")[:2]))

                if start_year_month <= file_year_month <= end_year_month:
                    file_path = os.path.join(csv_directory, filename)
                    df = pd.read_csv(file_path)

                    # Fetching specific columns from the request
                    columns = request.GET.getlist("columns")
                    if columns:
                        if report.date_col not in columns:
                            columns.append(report.date_col)
                        df = df[columns]

                    agg_data = pd.concat([agg_data, df], ignore_index=True)

    except FileNotFoundError:
        return JsonResponse(data={}, status=204)

    filtered_data = pd.DataFrame()

    if not agg_data.empty:
        filtered_data = agg_data[
            (agg_data[report.date_col] >= start_date)
            & (agg_data[report.date_col] <= end_date)
        ]

    if not filtered_data.empty:
        result = filtered_data.sort_values(report.date_col).to_json(orient="records")
    else:
        result = "[]"

    return JsonResponse(
        result,
        safe=False,
    )


@login_required
def view_filtered_data(request, report_id=None):
    report = Report.objects.filter(
        Q(access_users=request.user) | Q(access_groups__in=request.user.groups.all()),
        id=report_id,
    ).first()

    if not report:
        raise Http404("Invalid input provided.")

    if report.is_masterdata:
        return JsonResponse(
            {"error": "Masterdata cannot be filtered, since date column missing."},
            status=406,
        )

    interval = request.GET.get("interval")

    if interval:
        if interval not in ["day", "week", "month", "year"]:
            return JsonResponse({"error": "Invalid interval provided."}, status=400)
        start_date, end_date = commonutil.get_interval_date_str(interval)

    else:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not start_date or not end_date:
            return JsonResponse(
                {
                    "error": "Start date and end date required when interval is not provided."
                },
                status=400,
            )
    # start_date = "2024-05-01"
    start_year_month = tuple(map(int, start_date.split("-")[:2]))  # (year, month)
    end_year_month = tuple(map(int, end_date.split("-")[:2]))  # (year, month)

    csv_directory = settings.CSV_DIR / report.service_name

    agg_data = pd.DataFrame()

    try:
        for filename in os.listdir(csv_directory):
            if filename.endswith(".csv"):
                # Remove ".csv" extension
                file_year_month = tuple(map(int, filename[:-4].split("_")[:2]))

                if start_year_month <= file_year_month <= end_year_month:
                    file_path = os.path.join(csv_directory, filename)
                    df = pd.read_csv(file_path)
                    agg_data = pd.concat([agg_data, df], ignore_index=True)

    except FileNotFoundError:
        return JsonResponse(data={}, status=204)

    filtered_data = pd.DataFrame()

    if not agg_data.empty:
        filtered_data = agg_data[
            (agg_data[report.date_col] >= start_date)
            & (agg_data[report.date_col] <= end_date)
        ]

    if not filtered_data.empty:
        func = getattr(report_logic, report.service_name, None)
        if func is None:
            func = getattr(report_logic, "default", None)
        report_data = func(request, report, filtered_data)
    else:
        report_data = ""

    return JsonResponse({"data": report_data}, safe=False)
