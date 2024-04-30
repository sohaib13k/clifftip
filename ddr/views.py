import os
from django.http import HttpResponse
import gzip
from django.shortcuts import render
from django.conf import settings
import pandas as pd
import json
from .commonutil import append_total
from .models import CustomReport
from django.contrib.auth.decorators import login_required
from commonutil import commonutil

@login_required
def ddr(request):
    """
    View to show raw data file
    """
    rawdata_file_dir = settings.REPORT_DIR
    rawdata = [file.name for file in rawdata_file_dir.iterdir() if file.is_file()]
    rawdata_db = list(CustomReport.objects.values_list("name", flat=True))
    if rawdata_db:
        rawdata.append(rawdata_db)

    request.session["rawdata"] = (
        rawdata  # persisting data for re-use until session exists
    )

    return render(
        request,
        "ddr/ddr.html",
        {
            "rawdata": rawdata,
        },
    )


def temp(request, report):
    directory_path = settings.REPORT_DIR
    df_sales = pd.read_excel(report, skiprows=3)
    df_parties = pd.read_excel(directory_path / "sub_reports" / "All_Parties_DDR.xlsx")
    df_itemtype = pd.read_excel(directory_path / "sub_reports" / "Item Type Finished Goods.xlsx")

    # gstn_index = df_sales.columns.get_loc("Customer GSTN") + 1
    # df_sales.insert(gstn_index, 'Item Type', '0')

    updated_sales = pd.merge(
        df_sales,
        df_parties[["GST", "Sales Person", "Branch"]],
        left_on="Customer GSTN",
        right_on="GST",
        how="inner",
    )

    updated_sales = pd.merge(
        updated_sales,
        df_itemtype[["Item Type", "Item Code"]],
        on="Item Code",
        how="inner",
    )

    updated_sales = updated_sales.drop("GST", axis="columns")
    updated_sales = updated_sales[updated_sales["Branch"] != 0]
    updated_sales = updated_sales[updated_sales["Sales Person"] != 'General ID']

    report_excel = updated_sales.to_html(
        classes="table table-striped", index=False, header=True
    )
    report_excel_json = updated_sales.to_json(orient="records")

    temp = updated_sales.to_json(orient="table")
    output_directory = settings.BASE_DIR.parent / "data" / "json" / "report"
    os.makedirs(output_directory, exist_ok=True)
    compressed_file_path = output_directory / "data.json.gz"
    with gzip.open(compressed_file_path, "wt", encoding="utf-8") as compressed_file:
        compressed_file.write(temp)

    # Aggregating sales values
    individual_sales = (
        updated_sales.groupby("Sales Person").agg({"Net Total": "sum"}).reset_index()
    )
    individual_sales = append_total(
        individual_sales, "Sales Person", "Net Total"
    )

    branch_sales = (
        updated_sales.groupby("Branch").agg({"Net Total": "sum"}).reset_index()
    )
    branch_sales = append_total(branch_sales, "Branch", "Net Total")

    item_type_sales = (
        updated_sales.groupby("Item Type").agg({"Net Total": "sum"}).reset_index()
    )

    # import locale
    # locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    #
    # def format_currency(value):
    #     return locale.format_string("%d", value, grouping=True)

    item_type_sales = append_total(item_type_sales, "Item Type", "Net Total")
    # item_type_sales['Net Total'] = item_type_sales['Net Total'].apply(format_currency)


    individual_by_item_type_sales = (
        updated_sales.groupby(["Sales Person", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(
            fill_value=0)
    )

    branch_by_item_type_sales = (
        updated_sales.groupby(["Branch", "Item Type"])
        .agg({"Net Total": "sum"})
        .unstack(fill_value=0)
    )


    # formatting numbers as per locale
    # format_currency
    individual_sales['Net Total'] = individual_sales['Net Total'].apply(commonutil.format_rupees)
    branch_sales['Net Total'] = branch_sales['Net Total'].apply(commonutil.format_rupees)
    item_type_sales['Net Total'] = item_type_sales['Net Total'].apply(commonutil.format_rupees)

    for column in individual_by_item_type_sales.columns:  # Skip the first column
        individual_by_item_type_sales[column] = individual_by_item_type_sales[column].apply(commonutil.format_rupees)

    for column in branch_by_item_type_sales.columns:  # Skip the first column
        branch_by_item_type_sales[column] = branch_by_item_type_sales[column].apply(commonutil.format_rupees)


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
    
    render_data = render(
        request,
        "ddr/view_report.html",
        {
            "report": report.name,
            # "total": total,
            # "threshhold": threshhold,
            # "result": result,
            # "average": average,
            "report_excel": report_excel,
            "report_excel_json": report_excel_json,
            "sales_analysis": sales_analysis,
            "branch_analysis": branch_analysis,
            "item_type_analysis": item_type_analysis,
            "individual_by_item_type_analysis": individual_by_item_type_analysis,
            "branch_by_item_type_analysis": branch_by_item_type_analysis,
            "all_chart_data_json": all_chart_data_json,
            "myRange": range(1),
        },
    )

    return render_data

    # with open(settings.BASE_DIR.parent / "data" / "html" / 'html.html', 'r') as f:
    #     return HttpResponse(f.read(), content_type="text/html")

@login_required
def view_report(request, report):
    report = settings.REPORT_DIR / report

    if report.name == "Sale_Register_DDR.xlsx":
        return temp(request, report)

    # func = getattr(__service__, report.lower())

    # report_logic.func()

    # df = pd.read_excel(report, header=3, index_col=0)

    try:
        # total = df.at["Total", "Amount"]
        # df = pd.read_excel(report, header=3)
        # total_entries = df["Sr. No."].apply(lambda x: isinstance(x, (int, float))).sum()
        # threshhold = 30000
        # result = ""

        # match = re.search(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", total)

        # if match:
        #     numerical_value = match.group(0).replace(",", "")
        #     numerical_value = float(numerical_value)
        # else:
        #     numerical_value = None

        # average = numerical_value / total_entries

        # df = pd.read_excel(report, header=None).drop(index=[0, 1, 2])
        df = pd.read_excel(report, header=3)
        report_excel = df.to_html(
            classes="table table-striped", index=False, header=False
        )

        # if average < threshhold:
        #     result = "Sales average low that the set threshhold"
        return render(
            request,
            "ddr/view_report.html",
            {
                "report": report.name,
                # "total": total,
                # "threshhold": threshhold,
                # "result": result,
                # "average": average,
                "report_excel": report_excel,
            },
        )
    except KeyError as e:
        # TODO: add logger
        print(f"Key error: {e} - Check if the specified row or column exists.")
