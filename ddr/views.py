from django.core.cache import caches
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from report.models import Report
from account.models import UserProfile
from ddr.service import report_logic


@login_required
def ddr(request):
    accessible_reports = Report.get_accessible_reportlist(request.user)

    cached_param = request.GET.get("cached", None)
    file_cache = caches["file_based"]

    result = {}

    for report in accessible_reports:
        cache_key = f"preprocessed_report_data_ddr_{report.id}"

        if cached_param is not None and cached_param.lower() == "false":
            file_cache.delete(cache_key)

        report_data = file_cache.get(cache_key)

        service_name = report.service_name

        if report_data is None:
            func = getattr(report_logic, service_name, None)
            if func is None:
                func = getattr(report_logic, "default", None)
            report_data = func(request, report)

            file_cache.set(cache_key, report_data, timeout=604800)  # Cache for 7 days

        result[service_name] = report_data

    user_theme = UserProfile.objects.get(user=request.user).color_theme

    return render(
        request,
        "ddr/ddr.html",
        {
            "result": result,
            "theme": user_theme,
            "page":"ddr"
        },
    )
