from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from pathlib import Path
import pandas as pd
import tempfile
from django.core.files.storage import FileSystemStorage
from report.service import data_frame
from .models import Report
from commonutil import commonutil
from report.service import report_logic, upload_check
import logging


logger = logging.getLogger(__name__)


@login_required
def report(request):
    """
    View to fetch assigned reports
    """
    accessible_reports = Report.get_accessible_reportlist(request.user, include_custom_report=True)

    return render(
        request,
        "report/other/report.html",
        {
            "accessible_reports": accessible_reports,
        },
    )


# TODO: verify function name using regex- only alphanumeric with space allowed
@login_required
def upload(request):
    accessible_reports = Report.get_accessible_reportlist(request.user)
    # TODO: not sure why is_custom_report is set to false here
    # all_reports = request.user.accessible_reports_users.filter(is_custom_report=False)
    if request.method != "POST" or "excel_file" not in request.FILES:
        return render(
            request,
            "report/other/upload_report.html",
            {"all_reports": accessible_reports},
        )

    excel_file = request.FILES["excel_file"]
    # TODO: add this check in front end too
    if not excel_file.name.endswith((".xls", ".xlsx")):
        return HttpResponse("Invalid file format. Please upload an Excel file.")

    report_id = request.POST.get("report_id")
    report = all_reports.get(id=report_id)

    if report.name is None:
        logger.error("Report name missing, even though it's a required field in table")
        return HttpResponse("Report name could not be found. Please check with admin")

    file_size_mb = excel_file.size / 1024 / 1024  # Convert bytes to megabytes
    if not can_upload_file(file_size_mb, request.user):
        return HttpResponse(
            f"You've exhausted your {request.user.profile.storage_limit} Mb storage limit. Kindly check with admin."
        )

    file_path = settings.REPORT_DIR / report.service_name / excel_file.name

    if file_path.exists():
        ext = Path(excel_file.name).suffix
        unique_suffix = commonutil.get_unique_filename()
        new_path = (
            Path(settings.REPORT_DIR)
            / report.service_name
            / f"{Path(excel_file.name).stem}_{unique_suffix}.bak{ext}"
        )
        file_path.rename(new_path)

    temp_file_path = upload_excel_temp(excel_file)

    response = save_as_csv(report, temp_file_path)
    if isinstance(response, HttpResponse):
        return response

    commonutil.uploaded_excel(excel_file, settings.REPORT_DIR / report.service_name)

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
    # temp_file_path = os.path.join(temp_dir, excel_file.name)

    # Save the file to the temporary directory
    fs = FileSystemStorage(location=temp_dir)
    filename = fs.save(excel_file.name, excel_file)
    full_path = fs.path(filename)
    return Path(full_path)


# TODO: fix duplicate data issue. If same report uploaded again then data appending
def save_as_csv(report, excel_path):
    file_path = settings.CSV_DIR / report.service_name
    Path(file_path).mkdir(parents=True, exist_ok=True)

    func = getattr(data_frame, report.service_name, None)

    # routing to a default view for temp. upload
    if func is None:
        func = getattr(data_frame, "default", None)

    df = func(excel_path)

    if report.is_masterdata:
        # uploaded report column/date check
        func = getattr(upload_check, report.service_name, None)
        if func is not None:
            response = func(df)
            if isinstance(response, HttpResponse):
                return response

        file_name = report.service_name + ".csv"
        csv_file_path = file_path / file_name

        if csv_file_path.exists():
            ext = Path(file_name).suffix
            unique_suffix = commonutil.get_unique_filename()
            new_path = file_path / f"{Path(file_name).stem}_{unique_suffix}.bak{ext}"
            csv_file_path.rename(new_path)

        df.to_csv(csv_file_path, mode="w", header=True, index=False)
    else:
        try:
            df[report.date_col] = pd.to_datetime(df[report.date_col])
        except KeyError:
            return HttpResponse(
                f'Uploaded report doesn\'t contain "{report.date_col}" column. Kindly upload the right report',
                status=404,
            )
        df["Year"] = df[report.date_col].dt.year
        df["Month"] = df[report.date_col].dt.month

        grouped = df.groupby(["Year", "Month"])

        for (year, month), group in grouped:
            # Format filename as 'YYYY_MM.csv'
            filename = f"{int(year)}_{int(month):02d}.csv"
            csv_file_path = file_path / filename

            # Check if file already exists
            if csv_file_path.exists():
                group.to_csv(csv_file_path, mode="a", header=False, index=False)
            else:
                group.to_csv(csv_file_path, mode="w", header=True, index=False)


@login_required
def view_report(request, report_id):
    if not Report.is_report_accessible(report_id, request.user):
        return HttpResponse("Invalid report id passed.")

    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return HttpResponse(
            "Report name could not be found. Please check the report ID."
        )
    except Report.MultipleObjectsReturned:
        # TODO: handle this scenario, when multiple objects returned
        return HttpResponse("Multiple reports found. Please contact with admin.")

    template = report.service_name
    func = getattr(report_logic, report.service_name, None)

    if func is None:
        template = "default"
        func = getattr(report_logic, "default", None)

    result = func(request, report)

    return render(
        request,
        f"report/{template}.html",
        {"result": result},
    )
