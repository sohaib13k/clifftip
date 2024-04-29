from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from commonutil import commonutil
from django.http import HttpResponse
from django.urls import reverse
from .models import Report
from pathlib import Path

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
        all_reports = Report.objects.values_list('id', 'name')
        report_id = request.POST.get("report_id")
        report_id = int(report_id) if report_id.isdigit() else None

        report_exists = any(report_id == report[0] for report in all_reports)

        if not report_exists:
            add_url = reverse("report-add")
            return HttpResponse(
                f"This is an invalid report. Kindly add any new report before uploading <hr> <a href='{add_url}'>Report Metadata (add)</a>"
            )

        report_name = next((report[1] for report in all_reports if report_id == report[0]), None)
        if report_name is None:
            return HttpResponse("Report name could not be found. Please check the report ID.")
        
        file_path = settings.REPORTS_DIR / report_name / excel_file.name

        # print(">>>>>>>>>>>>>>>>", file_path)
        if file_path.exists():
            ext = Path(excel_file.name).suffix
            unique_suffix = commonutil.get_unique_filename()
            new_path = Path(settings.REPORTS_DIR) / report_name / f"{Path(excel_file.name).stem}_{unique_suffix}.bak{ext}"
            file_path.rename(new_path)

        commonutil.uploaded_excel(excel_file, settings.REPORTS_DIR / report_name)
        upload_url = reverse("report-upload")
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

    created_by = request.user.username
    is_masterdata = "is_masterdata" in request.POST

    if is_masterdata:
        name = request.POST.get("name")
        is_masterdata = 1
        is_datetime_merged, date_col, time_col = (None,) * 3
    else:
        name = request.POST.get("name")
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
