from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from ..models import (
    AllPartiesSelectedColumns,
    AllPartiesThreshold,
    BomReportOldDataVisibility,
    RoutingReportOldDataVisibility,
)
import json
import logging

logger = logging.getLogger("__name__")


@login_required
def saveEntity(request):
    # TODO: add authorisation check, like report/api/views.py/view_filtered_excel(...)
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    request_body = json.loads(request.body)

    method_name = request_body.get("methodName")
    func = globals().get(method_name)
    if func is None:
        return JsonResponse({"status": "error"}, status=400)

    result = func(request, request_body)
    return result


def save_all_parties_ddr_selected_columns(request, request_body):
    try:
        selected_columns = request_body.get("columns", [])

        # Save or update the selected columns for the user
        selected_columns_record, created = (
            AllPartiesSelectedColumns.objects.get_or_create(user=request.user)
        )
        selected_columns_record.columns = json.dumps(selected_columns)
        selected_columns_record.save()

        return JsonResponse({"status": "success", "message": selected_columns})

    except:
        return JsonResponse({"status": "error"})


def save_all_parties_ddr_threshold(request, request_body):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authenticated.")

    thresholds = request_body.get("threshold", {})

    threshold_obj = AllPartiesThreshold.objects.first()
    if not threshold_obj:
        threshold_obj = AllPartiesThreshold()
    threshold_obj.danger = thresholds.get("danger", 0)
    threshold_obj.action = thresholds.get("action", 0)
    threshold_obj.acceptable = thresholds.get("acceptable", 0)
    threshold_obj.save()

    return JsonResponse({"status": "success", "threshold": thresholds})


def save_bom_report_visibility_count(request, request_body):
    try:
        visibility_count = request_body.get("visibility_count", None)

        selected_columns_record, created = (
            BomReportOldDataVisibility.objects.get_or_create(user=request.user)
        )
        selected_columns_record.count = int(visibility_count)
        selected_columns_record.save()

        return JsonResponse({"status": "success", "message": visibility_count})

    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": "error"}, status=500)


def save_routing_report_visibility_count(request, request_body):
    try:
        visibility_count = request_body.get("visibility_count", None)

        selected_columns_record, created = (
            RoutingReportOldDataVisibility.objects.get_or_create(user=request.user)
        )
        selected_columns_record.count = int(visibility_count)
        selected_columns_record.save()

        return JsonResponse({"status": "success", "message": visibility_count})

    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": "error"}, status=500)
