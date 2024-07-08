import numpy as np
from django.http import Http404
from django.shortcuts import render
import pandas as pd
import gzip
import json
import os
from commonutil import commonutil
from report.commonutil import append_total, add_percentage_column
from django.conf import settings
from ..models import Report


def default(request, report):
    latest_file = commonutil.get_latest_csv_from_dir(report)

    df = pd.DataFrame()
    if latest_file is not None:
        df = pd.read_csv(latest_file)

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": df.to_json(orient="records"),
        "report": report,
    }

    return result


def sale_register(request, report):
    # file_path = settings.REPORT_DIR / report.service_name
    # latest_file = max(file_path.glob("*.xlsx"), key=lambda x: x.stat().st_mtime)
    # return temp(request, latest_file)

    # latest_file = commonutil.get_latest_csv_from_dir(report)

    # df = pd.DataFrame()
    # if latest_file is not None:
    #     df = pd.read_csv(latest_file)

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        # "data": df.to_json(orient="records"),
        "report": report,
    }

    return result


def all_parties(request, report):
    latest_file = commonutil.get_latest_csv_from_dir(report)

    df = pd.DataFrame()
    if latest_file is not None:
        df = pd.read_csv(latest_file, low_memory=False)

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": df.to_json(orient="records"),
        "report": report,
    }

    return result


def item_type_finished_goods(request, report):
    latest_file = commonutil.get_latest_csv_from_dir(report)

    df = pd.DataFrame()
    if latest_file is not None:
        df = pd.read_csv(latest_file)

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": df.to_json(orient="records"),
        "report": report,
    }

    return result


def routing_report(request, report, df=None):
    if df is None:
        latest_file = commonutil.get_latest_csv_from_dir(report)

        df = pd.DataFrame()
        if latest_file is not None:
            df = pd.read_csv(latest_file)
        
    lock_counts = df["Lock/Unlock"].value_counts().to_dict()
    locked_count = lock_counts.get("Lock", 0)
    unlocked_count = lock_counts.get("Unlock", 0)

    total_count = locked_count + unlocked_count

    locked_percent = (locked_count / total_count) * 100 if total_count != 0 else 0
    unlocked_percent = (unlocked_count / total_count) * 100 if total_count != 0 else 0

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": df.to_json(orient="records"),
        "data_lock": locked_count,
        "data_unlock": unlocked_count,
        "data_lock_percent": locked_percent,
        "data_unlock_percent": unlocked_percent,
        "report": report,
    }

    return result


def bom_report(request, report, df=None):
    if df is None:
        latest_file = commonutil.get_latest_csv_from_dir(report)

        df = pd.DataFrame()
        if latest_file is not None:
            df = pd.read_csv(latest_file)

    lock_counts = df["Lock/Unlock"].value_counts().to_dict()
    locked_count = lock_counts.get("Lock", 0)
    unlocked_count = lock_counts.get("Unlock", 0)

    total_count = locked_count + unlocked_count

    locked_percent = (locked_count / total_count) * 100 if total_count != 0 else 0
    unlocked_percent = (unlocked_count / total_count) * 100 if total_count != 0 else 0

    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": df.to_json(orient="records"),
        "data_lock": locked_count,
        "data_unlock": unlocked_count,
        "data_lock_percent": locked_percent,
        "data_unlock_percent": unlocked_percent,
        "report": report,
    }

    return result


def churn_rate(request, report):
    sale_purchase_model = Report.objects.get(service_name='sale_purchase')
    all_parties_model = Report.objects.get(service_name='all_parties')

    sale_purchase_csv = commonutil.get_latest_csv_from_dir(sale_purchase_model)
    all_parties_csv = commonutil.get_latest_csv_from_dir(all_parties_model)
    
    merged_df = pd.DataFrame()
    
    if sale_purchase_csv is not None and all_parties_csv  is not None:
        sales_prsn_filtered_parties = pd.read_csv(sale_purchase_csv).groupby("Sales Person")["Customer Name"].nunique().reset_index(name='Count as per filter')
        sales_prsn_total_parties = pd.read_csv(all_parties_csv).groupby("Sales Person")["Company Name"].size().reset_index(name='All parties')

        merged_df = pd.merge(sales_prsn_filtered_parties, sales_prsn_total_parties, on="Sales Person")

        merged_df['Ratio'] =((1 - (merged_df['Count as per filter'] / merged_df['All parties']))*100).round(1).astype(str)+'%'

        from report.views import save_as_csv
        save_as_csv(report, None, merged_df)
    
    result = {
        # "table": df.to_html(classes="table table-striped", index=False, header=False),
        "data": merged_df.to_json(orient="records"),
        "report": report,
    }

    return result


def temp(request, report):
    directory_path = settings.REPORT_DIR
    sale_reg_csv_dir = settings.CSV_DIR / "sale_register"
    df_sales = pd.DataFrame()

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
        df_parties = pd.read_csv(all_parties_csv, usecols=["Company Name", "Sales Person", "Branch.1"], low_memory=False)

    itemtype_csv = commonutil.get_latest_csv_from_dir(
        Report.objects.get(service_name="item_type_finished_goods")
    )

    if itemtype_csv is not None:
        df_itemtype = pd.read_csv(itemtype_csv, usecols=["Item Type", "Item Code"], low_memory=False)

    # gstn_index = df_sales.columns.get_loc("Customer GSTN") + 1
    # df_sales.insert(gstn_index, 'Item Type', '0')

    df_parties.rename(columns={"Branch.1":"Branch"}, inplace=True)

    df_parties_unique = df_parties.drop_duplicates(subset='Company Name', keep='first')

    updated_sales = pd.merge(
        df_sales,
        df_parties_unique,
        left_on="Customer Name",
        right_on="Company Name",
        how="left",
    )

    updated_sales = pd.merge(
        updated_sales,
        df_itemtype,
        on="Item Code",
        how="left",
    )

    updated_sales = updated_sales.drop("Company Name", axis="columns")
    # updated_sales = updated_sales[updated_sales["Branch"] != 0]

    updated_sales["Sales Person"] = updated_sales["Sales Person"].replace(np.nan, "(blank)").replace("", "(blank)")
    updated_sales["Branch"] = updated_sales["Branch"].replace(np.nan, "(blank)").replace("", "(blank)")
    updated_sales["Item Type"] = updated_sales["Item Type"].replace(np.nan, "(blank)").replace("", "(blank)")

    from report.views import save_as_csv
    save_as_csv(report, None, updated_sales)

    # report_excel = updated_sales.to_html(
    #     classes="table table-striped", index=False, header=True
    # )

    # Aggregating sales values
    individual_sales = (
        updated_sales.groupby("Sales Person").agg({"Net Total": "sum"}).reset_index()
    )
    individual_sales = append_total(individual_sales, "Sales Person", "Net Total")
    individual_sales = add_percentage_column(individual_sales, "Net Total")

    branch_sales = (
        updated_sales.groupby("Branch").agg({"Net Total": "sum"}).reset_index()
    )
    branch_sales = append_total(branch_sales, "Branch", "Net Total")
    branch_sales = add_percentage_column(branch_sales, "Net Total")

    item_type_sales = (
        updated_sales.groupby("Item Type").agg({"Net Total": "sum"}).reset_index()
    )
    item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    item_type_sales = add_percentage_column(item_type_sales, "Net Total")

    # import locale
    # locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    #
    # def format_currency(value):
    #     return locale.format_string("%d", value, grouping=True)

    # item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    # item_type_sales['Net Total'] = item_type_sales['Net Total'].apply(format_currency)

    individual_by_item_type_sales = (
        updated_sales.groupby(["Sales Person", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(fill_value=0)
    )

    branch_by_item_type_sales = (
        updated_sales.groupby(["Branch", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(fill_value=0)
    )

    # formatting numbers as per locale
    # format_currency
    individual_sales["Net Total"] = (
        individual_sales["Net Total"]
        .round()
        .astype(int)
        .apply(commonutil.format_rupees)
    )
    branch_sales["Net Total"] = (
        branch_sales["Net Total"].round().astype(int).apply(commonutil.format_rupees)
    )
    item_type_sales["Net Total"] = (
        item_type_sales["Net Total"].round().astype(int).apply(commonutil.format_rupees)
    )

    for column in individual_by_item_type_sales.columns:  # Skip the first column
        individual_by_item_type_sales[column] = (
            individual_by_item_type_sales[column]
            .round()
            .astype(int)
            .apply(commonutil.format_rupees)
        )

    for column in branch_by_item_type_sales.columns:  # Skip the first column
        branch_by_item_type_sales[column] = (
            branch_by_item_type_sales[column]
            .round()
            .astype(int)
            .apply(commonutil.format_rupees)
        )

    # Convert to HTML for displaying in the template
    sales_analysis = individual_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    branch_analysis = branch_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    item_type_analysis = item_type_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    individual_by_item_type_analysis = individual_by_item_type_sales.to_html(
        classes="table table-striped", index=True, header=True
    )
    branch_by_item_type_analysis = branch_by_item_type_sales.to_html(
        classes="table table-striped", index=True, header=True
    )

    # Preparing data for chart
    individual_chart_data = {
        "labels": individual_sales["Sales Person"].tolist()[
            :-1
        ],  # Excludes the 'Total' label
        "data": individual_sales["Net Total"].tolist()[
            :-1
        ],  # Excludes the 'Total' data
    }

    branch_chart_data = {
        "labels": branch_sales["Branch"].tolist()[:-1],  # Excludes the 'Total' label
        "data": branch_sales["Net Total"].tolist()[:-1],  # Excludes the 'Total' label
    }

    item_type_chart_data = {
        "labels": item_type_sales["Item Type"].tolist()[
            :-1
        ],  # Excludes the 'Total' label
        "data": item_type_sales["Net Total"].tolist()[
            :-1
        ],  # Excludes the 'Total' label
    }

    individual_item_type_datasets = []
    for item_type in individual_by_item_type_sales.columns:
        individual_item_type_datasets.append(
            {
                "label": item_type,
                "data": individual_by_item_type_sales[item_type].tolist()[
                    :-1
                ],  # Excludes the 'Total' data
            }
        )

    branch_item_type_datasets = []
    for item_type in branch_by_item_type_sales.columns:
        branch_item_type_datasets.append(
            {
                "label": item_type,
                "data": branch_by_item_type_sales[item_type].tolist()[
                    :-1
                ],  # Excludes the 'Total' data
            }
        )

    # passing all chart data in one serialized JSON object
    all_chart_data = {
        "individual_chart_data": individual_chart_data,
        "branch_chart_data": branch_chart_data,
        "item_type_chart_data": item_type_chart_data,
        "individual_by_item_type_chart_data": {
            "labels": individual_by_item_type_sales.index.tolist()[:-1],
            "datasets": individual_item_type_datasets,
        },
        "branch_by_item_type_chart_data": {
            "labels": branch_by_item_type_sales.index.tolist()[:-1],
            "datasets": branch_item_type_datasets,
        },
    }
    all_chart_data_json = json.dumps(all_chart_data)

    return {
        "report": report,
        # "total": total,
        # "threshhold": threshhold,
        # "result": result,
        # "average": average,
        # "report_excel": report_excel,
        "sales_analysis": sales_analysis,
        "branch_analysis": branch_analysis,
        "item_type_analysis": item_type_analysis,
        "individual_by_item_type_analysis": individual_by_item_type_analysis,
        "branch_by_item_type_analysis": branch_by_item_type_analysis,
        "all_chart_data_json": all_chart_data_json,
        "myRange": range(1),
    }


def sale_purchase(request, report):
    return temp(request, report)


def all_parties_with_sale(request, report, *args):
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
    
    from report.views import save_as_csv
    save_as_csv(report, None, parties_with_sale)

    if args and args[0] == "ddr":
        return {"df_parties_with_sale": parties_with_sale, "df_sales": df_sales}

    result = {
        "data": parties_with_sale.to_json(orient="records"),
        "report": report,
    }

    return result