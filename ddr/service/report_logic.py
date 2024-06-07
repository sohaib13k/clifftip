from django.http import Http404
from django.shortcuts import render
import pandas as pd
import gzip
import json
import os
from commonutil import commonutil
from report.commonutil import append_total, add_percentage_column
from report.service import report_logic
from django.conf import settings
from report.models import Report
from ddr.models import (
    AllPartiesSelectedColumns,
    AllPartiesThreshold,
    BomReportOldDataVisibility,
    RoutingReportOldDataVisibility,
)


def default(request, report):
    return report_logic.default(request, report)


def bom_report(request, report):
    visibility_count_obj = BomReportOldDataVisibility.objects.first()
    visibility_count = visibility_count_obj.count if visibility_count_obj else 7

    csv_dir = settings.CSV_DIR / report.service_name

    if not os.path.exists(csv_dir):
        result = {
            "items": [],
            "report": report,
        }
        return result

    csv_files = sorted(
        csv_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True
    )

    csv_files = csv_files[:visibility_count]

    items = []
    for file in csv_files:
        df = pd.read_csv(file)
        output = report_logic.bom_report(request, report, df)
        del output["data"]
        output["report_upload_date"] = pd.to_datetime(
            file.stat().st_ctime, unit="s"
        ).strftime("%d-%m-%Y")
        output["total"] = output["data_unlock"] + output["data_lock"]
        items.append(output)

    result = {
        "items": items,
        "visibility_count": visibility_count,
        "report": report,
    }

    return result


def routing_report(request, report):
    visibility_count_obj = RoutingReportOldDataVisibility.objects.first()
    visibility_count = visibility_count_obj.count if visibility_count_obj else 7

    csv_dir = settings.CSV_DIR / report.service_name

    if not os.path.exists(csv_dir):
        result = {
            "items": [],
            "report": report,
        }
        return result

    csv_files = sorted(
        csv_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True
    )

    csv_files = csv_files[:visibility_count]

    items = []
    for file in csv_files:
        df = pd.read_csv(file)
        output = report_logic.routing_report(request, report, df)
        del output["data"]
        output["report_upload_date"] = pd.to_datetime(
            file.stat().st_ctime, unit="s"
        ).strftime("%d-%m-%Y")
        output["total"] = output["data_unlock"] + output["data_lock"]
        items.append(output)

    result = {
        "items": items,
        "visibility_count": visibility_count,
        "report": report,
    }

    return result


def all_parties_with_sale(request, report):
    associated_reports = report.reports.filter(
        service_name__in=["sale_register", "all_parties"]
    )

    if len(associated_reports) < 2:
        return {report.service_name: "No associated data present"}

    df_sales = pd.DataFrame()
    df_parties = pd.DataFrame()

    sale_reg_csv_dir = settings.CSV_DIR / "sale_register"

    try:
        for filename in os.listdir(sale_reg_csv_dir):
            if filename.endswith(".csv"):
                file_path = os.path.join(sale_reg_csv_dir, filename)
                df = pd.read_csv(file_path)
                df_sales = pd.concat([df_sales, df], ignore_index=True)

    except FileNotFoundError:
        raise Http404("File not found.")

    all_parties_csv = commonutil.get_latest_csv_from_dir(
        Report.objects.get(service_name="all_parties")
    )

    if all_parties_csv is not None:
        df_parties = pd.read_csv(all_parties_csv, low_memory=False)

    parties_with_sale = pd.merge(
        df_parties,
        df_sales[["Customer Name"]],
        left_on="Company Name",
        right_on="Customer Name",
        how="inner",
    )

    parties_with_sale = parties_with_sale.drop_duplicates(subset=["Company Name"])
    parties_with_sale = parties_with_sale.drop(columns=["Customer Name"])

    selected_columns_record = AllPartiesSelectedColumns.objects.filter(
        user=request.user
    ).first()
    selected_columns = (
        json.loads(selected_columns_record.columns) if selected_columns_record else []
    )

    all_parties_thresholds = AllPartiesThreshold.objects.first()
    thresholds = all_parties_thresholds.__dict__ if all_parties_thresholds else {}
    counts = {}
    total_entries = len(parties_with_sale)
    for column in parties_with_sale.columns:
        column_count = parties_with_sale[
            column
        ].count()  # Count of non-null values in the column
        difference = total_entries - column_count  # Difference from total entries
        counts[column] = difference if difference >= 0 else 0

    result = {
        "data": df_parties.to_json(orient="records"),
        "selected_columns": selected_columns,
        "counts": counts,
        "threshold": thresholds,
        "report": report,
    }

    return result
