from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from pathlib import Path
import pandas as pd
import gzip
import json
import os
import tempfile
from django.core.files.storage import FileSystemStorage
from report.service import data_frame
from .models import Report
from commonutil import commonutil
from .commonutil import append_total
from report.service import report_logic


@login_required
def report(request):
    """
    View to fetch assigned reports
    """
    user = request.user

    # Fetch reports directly accessible to the user, ensuring it is distinct
    direct_reports = user.accessible_reports_users.all().distinct()

    # Fetch reports accessible through user's groups, ensuring it is distinct
    group_reports = Report.objects.filter(
        access_groups__in=user.groups.all()
    ).distinct()

    # Combine both QuerySets without duplicates using the union operator
    accessible_reports = direct_reports.union(group_reports)

    return render(
        request,
        "report/report.html",
        {
            "accessible_reports": accessible_reports,
        },
    )


# TODO: verify function name using regex- only alphanumeric with space allowed
@login_required
def upload(request):
    all_reports = request.user.accessible_reports_users.filter(is_custom_report=False)
    if request.method != "POST" or "excel_file" not in request.FILES:
        return render(
            request, "report/upload_report.html", {"all_reports": all_reports}
        )

    excel_file = request.FILES["excel_file"]
    # TODO: add this check in front end too
    if not excel_file.name.endswith((".xls", ".xlsx")):
        return HttpResponse("Invalid file format. Please upload an Excel file.")

    report_id = request.POST.get("report_id")
    report = all_reports.get(id=report_id)

    report_name = report.name
    if report_name is None:
        # TODO: add logger in all places like this; to track error
        return HttpResponse(
            "Report name could not be found. Please check with admin"
        )

    file_size_mb = excel_file.size / 1024 / 1024  # Convert bytes to megabytes
    if not can_upload_file(file_size_mb, request.user):
        return HttpResponse(
            f"You've exhausted your {request.user.profile.storage_limit} Mb storage limit. Kindly check with admin."
        )

    file_path = settings.REPORT_DIR / report_name / excel_file.name

    if file_path.exists():
        ext = Path(excel_file.name).suffix
        unique_suffix = commonutil.get_unique_filename()
        new_path = (
            Path(settings.REPORT_DIR)
            / report_name
            / f"{Path(excel_file.name).stem}_{unique_suffix}.bak{ext}"
        )
        file_path.rename(new_path)

    temp_file_path = upload_excel_temp(excel_file)

    save_as_csv(report, temp_file_path)

    commonutil.uploaded_excel(excel_file, settings.REPORT_DIR / report_name)

    increment_file_upload_limit(file_size_mb, request.user)

    upload_url = reverse("report-upload")
    return HttpResponse(
        f"File uploaded successfully and saved! <hr> <a href='{upload_url}'>Upload more report</a>"
    )


def increment_file_upload_limit(file_size, user):
    profile = user.profile
    profile.used_storage += file_size
    profile.save()


def can_upload_file(file_size, user):
    profile = user.profile

    if profile.used_storage + file_size > profile.storage_limit:
        return False
    return True


def upload_excel_temp(excel_file):
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, excel_file.name)

    # Save the file to the temporary directory
    fs = FileSystemStorage(location=temp_dir)
    filename = fs.save(excel_file.name, excel_file)
    full_path = fs.path(filename)
    return Path(full_path)


# TODO: fix duplicate data issue. If same report uploaded again then data appending
def save_as_csv(report, excel_path):
    file_path = settings.CSV_DIR / report.name
    Path(file_path).mkdir(parents=True, exist_ok=True)

    func = getattr(data_frame, report.service_name, None)
    df = func(excel_path)

    if report.is_masterdata:
        file_name = report.name + ".csv"
        csv_file_path = file_path / file_name
        df.to_csv(csv_file_path, mode="w", header=True, index=False)
    else:
        df[report.date_col] = pd.to_datetime(df[report.date_col])
        df["Year"] = df[report.date_col].dt.year
        df["Month"] = df[report.date_col].dt.month

        grouped = df.groupby(["Year", "Month"])

        for (year, month), group in grouped:
            # Format filename as 'YYYY_MM.csv'
            filename = f"{year}_{month:02d}.csv"
            csv_file_path = file_path / filename

            # Check if file already exists
            if csv_file_path.exists():
                group.to_csv(csv_file_path, mode="a", header=False, index=False)
            else:
                group.to_csv(csv_file_path, mode="w", header=True, index=False)


def temp(request, report):
    directory_path = settings.REPORT_DIR
    df_sales = pd.read_excel(report, skiprows=3)
    df_parties = pd.read_excel(directory_path / "sub_reports" / "All_Parties_DDR.xlsx")
    df_itemtype = pd.read_excel(
        directory_path / "sub_reports" / "Item Type Finished Goods.xlsx"
    )

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
    updated_sales = updated_sales[updated_sales["Sales Person"] != "General ID"]

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
    individual_sales["Net Total"] = individual_sales["Net Total"].apply(
        commonutil.format_rupees
    )
    branch_sales["Net Total"] = branch_sales["Net Total"].apply(
        commonutil.format_rupees
    )
    item_type_sales["Net Total"] = item_type_sales["Net Total"].apply(
        commonutil.format_rupees
    )

    for column in individual_by_item_type_sales.columns:  # Skip the first column
        individual_by_item_type_sales[column] = individual_by_item_type_sales[
            column
        ].apply(commonutil.format_rupees)

    for column in branch_by_item_type_sales.columns:  # Skip the first column
        branch_by_item_type_sales[column] = branch_by_item_type_sales[column].apply(
            commonutil.format_rupees
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
def view_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return HttpResponse(
            "Report name could not be found. Please check the report ID."
        )
    except Report.MultipleObjectsReturned:
        # TODO: handle this scenario, when multiple objects returned
        return HttpResponse("Multiple reports found. Please contact with admin.")

    if report.name == "Sale_Register_DDR.xlsx":
        return temp(request, report)

    func = getattr(report_logic, report.service_name, None)
    response = func()
    return HttpResponse(response)

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


def add_percentage_column(df, total_col_name):
    total_sum = df[total_col_name].iloc[-1]  # Accessing the last element in the column
    if total_sum == 0:  # Avoid division by zero
        df["Percentage"] = 0
    else:
        # Calculate the percentage of each row relative to the total sum
        df["Percentage"] = (df[total_col_name] / total_sum * 100).round(2)
    return df
