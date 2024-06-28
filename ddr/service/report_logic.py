from django.http import HttpResponse, Http404
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
    parties_with_sale = report_logic.all_parties_with_sale(request, report, "ddr")[
        "df_parties_with_sale"
    ]
    sale_register_report = Report.objects.filter(service_name="sale_register").first()

    current_date = datetime.now()
    start_date = current_date - relativedelta(months=4)
    start_date = start_date.replace(day=1)

    merged_df = pd.DataFrame()
    count = 0
    sale_reg_csv_dir = settings.CSV_DIR / "sale_register"

    try:
        for filename in os.listdir(sale_reg_csv_dir):
            if filename.endswith(".csv") and count < 4:
                file_date = datetime.strptime(filename, "%Y_%m.csv")
                if start_date <= file_date <= current_date:
                    file_path = os.path.join(sale_reg_csv_dir, filename)
                    df = pd.read_csv(file_path)
                    merged_df = pd.concat([merged_df, df], ignore_index=True)
                    count += 1

    except Exception as e:
        return HttpResponse("", status=500)

    filtered_df = pd.DataFrame()

    if not merged_df.empty:
        # Convert the date column to datetime
        merged_df["Invoice Date"] = pd.to_datetime(merged_df["Invoice Date"])
        # Filter the DataFrame to include only the data from the last four months
        filtered_df = merged_df[
            (merged_df[sale_register_report.date_col] >= start_date)
            & (merged_df[sale_register_report.date_col] <= current_date)
        ]

    if not filtered_df.empty:
        common_gst_no = filtered_df["Customer GSTN"].unique()
        parties_with_sale_dead = parties_with_sale[
            ~parties_with_sale["GST No."].isin(common_gst_no)
        ]
    else:
        parties_with_sale_dead = parties_with_sale

    parties_with_sale_dead_count = parties_with_sale_dead.shape[0]

    # ==========================================================================================================

    current_date = datetime.now()
    current_date = (current_date.replace(day=1) - relativedelta(days=1)).date()

    # Open the CSV file for the previous month and get unique GST numbers
    file_path = sale_reg_csv_dir / f"{current_date.year}_{current_date.month:02d}.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        gst_numbers = set(df["Customer GSTN"].unique())
    else:
        gst_numbers = set()

    # Iterate through the previous three months
    for _ in range(3):
        current_date -= relativedelta(months=1)
        file_path = (
            sale_reg_csv_dir / f"{current_date.year}_{current_date.month:02d}.csv"
        )
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            previous_gst_numbers = set(df["Customer GSTN"].unique())
            gst_numbers = gst_numbers.intersection(previous_gst_numbers)

    parties_with_sale_on_off = parties_with_sale[
        ~parties_with_sale["GST No."].isin(gst_numbers)
    ]
    parties_with_sale_on_off = parties_with_sale_on_off[
        ~parties_with_sale_on_off["GST No."].isin(parties_with_sale_dead["GST No."])
    ]

    parties_with_sale_regular = parties_with_sale[
        parties_with_sale["GST No."].isin(gst_numbers)
    ]

    parties_with_sale_on_off_count = parties_with_sale_on_off.shape[0]
    parties_with_sale_regular_count = parties_with_sale_regular.shape[0]

    # ==========================================================================================================

    sale_pur_csv_dir = settings.CSV_DIR / "sale_purchase"

    current_date = datetime.now()
    current_date = (current_date.replace(day=1) - relativedelta(days=1)).date()

    sale_pur_df = pd.DataFrame()

    # Merge CSV files for the last four months
    for _ in range(4):
        file_path = (
            sale_pur_csv_dir / f"{current_date.year}_{current_date.month:02d}.csv"
        )
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            sale_pur_df = pd.concat([sale_pur_df, df], ignore_index=True)
        current_date -= relativedelta(months=1)

    # Group by 'Customer GSTN' and count unique 'Item_type'
    gst_item_counts = sale_pur_df.groupby("Customer GSTN")["Item Type"].nunique()
    # Filter GST numbers with more than one unique 'Item_type'
    gst_multiple_items = gst_item_counts[gst_item_counts > 1].index
    # Collect rows corresponding to these GST numbers
    parties_with_sale_cross_sales = sale_pur_df[
        sale_pur_df["Customer GSTN"].isin(gst_multiple_items)
    ]

    # TODO: Temp code, until below todo getting fixed.
    filtered_parties_with_sale = parties_with_sale[
        parties_with_sale["GST No."].isin(
            parties_with_sale_cross_sales["Customer GSTN"]
        )
    ]
    unique_parties_with_sale = filtered_parties_with_sale.drop_duplicates(
        subset="GST No."
    )
    unique_parties_with_sale = unique_parties_with_sale.sort_values(by="Company Name")

    # TODO: Fix handsontable issue, where 2 different structure on same page causing issue. Until then below code commented
    # parties_with_sale_cross_sales = parties_with_sale_cross_sales.sort_values(by='Customer Name')

    # # Reorder columns to place 'Item Type' beside 'Customer GSTN'
    # columns = list(parties_with_sale_cross_sales.columns)
    # columns.insert(columns.index('Customer GSTN') + 1, columns.pop(columns.index('Item Type')))
    # parties_with_sale_cross_sales = parties_with_sale_cross_sales[columns]

    # parties_with_sale_cross_sales_count = parties_with_sale_cross_sales['Customer GSTN'].nunique()

    # ==========================================================================================================

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

    # ==========================================================================================================

    result = {
        "data": parties_with_sale.to_json(orient="records"),
        "selected_columns": selected_columns,
        "counts": counts,
        "threshold": thresholds,
        "report": report,
        "parties_with_sale_dead_count": parties_with_sale_dead_count,
        "parties_with_sale_dead": parties_with_sale_dead.to_json(orient="records"),
        "parties_with_sale_on_off_count": parties_with_sale_on_off_count,
        "parties_with_sale_on_off": parties_with_sale_on_off.to_json(orient="records"),
        "parties_with_sale_regular_count": parties_with_sale_regular_count,
        "parties_with_sale_regular": parties_with_sale_regular.to_json(
            orient="records"
        ),
        "parties_with_sale_cross_sales": unique_parties_with_sale.to_json(
            orient="records"
        ),
        "parties_with_sale_cross_sales_count": len(unique_parties_with_sale),
    }

    return result


def invoice_report(request, report):
    invoice_csv_dir = settings.CSV_DIR / report.service_name
    current_date = datetime.now()
    current_date = (current_date.replace(day=1) - relativedelta(days=1)).date()

    report_data = {}

    for _ in range(4):
        month_key = current_date.strftime("%b")
        file_path = (
            invoice_csv_dir / f"{current_date.year}_{current_date.month:02d}.csv"
        )
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            delay_count = len(df[df["Delay Shipment Days"] > 0])
            on_time_count = len(df[df["Delay Shipment Days"] <= 0])

            report_data[month_key] = {
                "delay_count": delay_count,
                "on_time_count": on_time_count,
            }

        current_date -= relativedelta(months=1)

    result = {"data": report_data, "report": report}

    return result
