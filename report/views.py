from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from commonutil import commonutil
from django.http import HttpResponse
from django.urls import reverse
from .models import Report
from pathlib import Path
import pandas as pd
from report.service import data_frame


@login_required
def report(request):
    return render(request, "report/report.html")


# TODO: verify function name using regex- only alphanumeric with space allowed
@login_required
def upload(request):
    all_reports = request.user.accessible_reports_users.all()
    if request.method != "POST" or "excel_file" not in request.FILES:
        return render(
            request, "report/upload_report.html", {"all_reports": all_reports}
        )

    excel_file = request.FILES["excel_file"]
    # TODO: add this check in front end too
    if not excel_file.name.endswith((".xls", ".xlsx")):
        return HttpResponse("Invalid file format. Please upload an Excel file.")

    try:
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

        commonutil.uploaded_excel(excel_file, settings.REPORT_DIR / report_name)

        save_as_csv(report, file_path)

        increment_file_upload_limit(file_size_mb, request.user)

        upload_url = reverse("report-upload")
        return HttpResponse(
            f"File uploaded successfully and saved! <hr> <a href='{upload_url}'>Upload more report</a>"
        )

    except Exception as e:
        return HttpResponse(f"Error saving Excel file: {str(e)}")


def increment_file_upload_limit(file_size, user):
    profile = user.profile
    profile.used_storage += file_size
    profile.save()


def can_upload_file(file_size, user):
    profile = user.profile

    if profile.used_storage + file_size > profile.storage_limit:
        return False
    return True


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
