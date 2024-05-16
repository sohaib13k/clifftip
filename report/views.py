from django.core.cache import caches
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils import timezone
from pathlib import Path
import pandas as pd
import tempfile
from django.core.files.storage import FileSystemStorage
from report.service import data_frame
from .models import Report, Employee
from commonutil import commonutil
from report.service import report_logic, upload_check
import logging
import os
import csv
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from account.models import UserProfile

logger = logging.getLogger(__name__)


@login_required
def report(request):
    """
    View to fetch assigned reports
    """
    accessible_reports = Report.get_accessible_reportlist(
        request.user
    )

    return render(
        request,
        "report/other/report.html",
        {
            "accessible_reports": accessible_reports,
            "theme": UserProfile.objects.get(user=request.user).color_theme,
        },
    )


# TODO: verify function name using regex- only alphanumeric with space allowed
@login_required
def upload(request):
    accessible_reports = Report.get_accessible_reportlist(
        request.user
    )
    if request.method != "POST":
        sales_person = Employee.objects.filter(job_title="SE")

        return render(
            request,
            "report/other/upload_report.html",
            {
                "accessible_reports": accessible_reports,
                "sales_person": sales_person,
                "theme": UserProfile.objects.get(user=request.user).color_theme,
            },
        )

    if request.POST.get('form_type') == 'form_entry':
        upload_form(request)
        upload_url = reverse("report-upload")
        return HttpResponse(
            f"Data successfully saved! <hr> <a href='{upload_url}'>Upload more report</a>"
        )


    if request.POST.get('form_type') != 'excel_upload' or "excel_file" not in request.FILES:
        return render(
            request,
            "report/other/upload_report.html",
            {"accessible_reports": accessible_reports},
        )

    excel_file = request.FILES["excel_file"]
    # TODO: add this check in front end too
    if not excel_file.name.endswith((".xls", ".xlsx")):
        return HttpResponse("Invalid file format. Please upload an Excel file.")

    report_id = request.POST.get("report_id")
    report = accessible_reports.get(id=report_id)

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
        commonutil.rename_file_with_unique_suffix(
            file_path, excel_file.name, settings.REPORT_DIR, report
        )

    temp_file_path = upload_excel_temp(excel_file)

    response = save_as_csv(report, temp_file_path)
    if isinstance(response, HttpResponse):
        return response
    # TODO: above temp can now be deleted

    commonutil.uploaded_excel(excel_file, settings.REPORT_DIR / report.service_name)

    increment_file_upload_limit(file_size_mb, request.user)

    report.report_last_updated_tmstmp = timezone.now()
    report.save(update_fields=['report_last_updated_tmstmp'])

    upload_url = reverse("report-upload")
    return HttpResponse(
        f"File uploaded successfully and saved! <hr> <a href='{upload_url}'>Upload more report</a>"
    )

def upload_form(request):
    sales_person = Employee.objects.filter(job_title="SE").order_by('id')
    report = Report.objects.get(service_name=request.POST.get('report'))
    date = request.POST.get('reportDate')
    data = []

    # Assuming 'sales_person' is a list of employee objects available in the context
    for person in sales_person:
        person_id = str(person.id)  # Make sure it's a string, suitable for dictionary keys
        person_value = request.POST.get(person_id, '')
        data.append(person_value)

    file_path = settings.CSV_DIR / report.service_name
    Path(file_path).mkdir(parents=True, exist_ok=True)

    file_path = file_path / (report.service_name + ".csv")

    if not file_path.exists():
        headers = ['Date'] + [person for person in sales_person]

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow([date] + data)

    else:
        new_headers  = ['Date'] + [person for person in sales_person]

        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            current_headers = next(reader, [])  # Read the first row, which contains headers
            all_data = list(reader)  # Read the rest of the data

        # Compare current headers with new headers
        if set(current_headers) != set(new_headers):
            # If they are different, write new headers and all existing data plus the new row
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(new_headers)
                writer.writerows(all_data)
                writer.writerow([date] + data)
        else:
            # If headers are the same, just append the new row
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([date] + data)


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
def save_as_csv(report, excel_path, df=None):
    file_path = settings.CSV_DIR / report.service_name
    Path(file_path).mkdir(parents=True, exist_ok=True)

    func = getattr(data_frame, report.service_name, None)

    # routing to a default view for temp. upload
    if func is None:
        func = getattr(data_frame, "default", None)

    if df is None:
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

        # TODO: replace this with commonutil.rename_file_with_unique_suffix(...)
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

            group.drop(columns=["Year", "Month"], inplace=True)

            # if csv_file_path.exists():
            #     group.to_csv(csv_file_path, mode="a", header=False, index=False)
            # else:
            group.to_csv(csv_file_path, mode="w", header=True, index=False)


@login_required
def view_report(request, report_id):
    if not Report.is_report_accessible(report_id, request.user):
        logger.debug(msg="Invalid report id passed.")
        raise Http404

    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        logger.debug(msg="Report name could not be found. Please check the report ID.")
        raise Http404
    except Report.MultipleObjectsReturned:
        # TODO: handle this scenario, when multiple objects returned
        logger.error(msg="Multiple reports found. Please contact with admin.")
        raise Exception

    service_name = report.service_name
    cached_param = request.GET.get("cached", None)
    user_theme = UserProfile.objects.get(user=request.user).color_theme

    cache_key = f"preprocessed_report_data_{report_id}"
    file_cache = caches['file_based']

    if cached_param is not None and cached_param.lower() == "false":
        file_cache.delete(cache_key)

    report_data = file_cache.get(cache_key)
    if report_data is None:
        func = getattr(report_logic, service_name, None)
        if func is None:
            func = getattr(report_logic, "default", None)
        report_data = func(request, report)

        file_cache.set(cache_key, report_data, timeout=604800)  # Cache for 7 days

    try:
        get_template(f"report/{service_name}.html")
        template = f"report/{service_name}.html"
    except TemplateDoesNotExist:
        template = f"report/default.html"

    return render(
        request,
        template,
        {
            "result": report_data,
            "theme": user_theme,
        },
    )
