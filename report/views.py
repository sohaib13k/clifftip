from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from commonutil import commonutil
from django.http import HttpResponse
from django.urls import reverse
from .models import Report
from pathlib import Path
import pandas as pd


@login_required
def report(request):
    return render(request, "report/report.html")


@login_required
def upload(request):
    if request.method != "POST" or "excel_file" not in request.FILES:
        all_reports = list(Report.objects.all())
        return render(
            request, "report/upload_report.html", {"all_reports": all_reports}
        )

    excel_file = request.FILES["excel_file"]
    # TODO: add this check in front end too
    if not excel_file.name.endswith((".xls", ".xlsx")):
        return HttpResponse("Invalid file format. Please upload an Excel file.")

    try:
        all_reports = Report.objects.values_list("id", "name")
        report_id = request.POST.get("report_id")
        report_id = int(report_id) if report_id.isdigit() else None

        report_exists = any(report_id == report[0] for report in all_reports)

        if not report_exists:
            add_url = reverse("report-add")
            return HttpResponse(
                f"This is an invalid report. Kindly add any new report before uploading <hr> <a href='{add_url}'>Report Metadata (add)</a>"
            )

        report_name = next(
            (report[1] for report in all_reports if report_id == report[0]), None
        )
        if report_name is None:
            return HttpResponse(
                "Report name could not be found. Please check the report ID."
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

        commonutil.uploaded_excel(excel_file, settings.REPORT_DIR / report_name)
        upload_url = reverse("report-upload")
        parse_and_save_excel(file_path, report_name)
        return HttpResponse(
            # TODO: add logger
            f"File uploaded successfully and saved! <hr> <a href='{upload_url}'>Upload more report</a>"
        )

    except Exception as e:
        # TODO: add logger
        return HttpResponse("Error saving Excel file: " + str(e))


@login_required
def add(request):
    if request.method != "POST":
        return render(request, "report/add_report.html")

    name = request.POST.get("name")
    all_reports = Report.objects.values_list("name")
    report_exists = any(name == report[0] for report in all_reports)

    if report_exists:
        return HttpResponse(f"This report already exists.")

    created_by = request.user.username
    is_masterdata = "is_masterdata" in request.POST

    if is_masterdata:
        is_masterdata = 1
        is_datetime_merged, date_col, time_col = (None,) * 3
    else:
        is_masterdata = 0
        date_col = request.POST.get("date_col")
        time_col = request.POST.get("time_col")
        is_datetime_merged = "is_datetime_merged" in request.POST

    report = Report(
        name=name,
        is_masterdata=is_masterdata,
        is_datetime_merged=is_datetime_merged,
        date_col=date_col,
        time_col=time_col,
        created_by=created_by,
    )
    report.save()

    return HttpResponse("Report created successfully!")


# TODO: fix duplicate data issue. If same report uploaded again then data appending
def parse_and_save_excel(excel_path, report_name):
    file_path = settings.JSON_DIR / report_name
    Path(file_path).mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(excel_path, engine="openpyxl", skiprows=3)
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])
    df["Year"] = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.month

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
