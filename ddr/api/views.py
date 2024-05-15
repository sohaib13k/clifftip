from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import SelectedColumns
import json


@login_required
@csrf_protect
def saveEntity(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    request_body = json.loads(request.body)

    method_name = request_body.get("methodName")
    func = globals().get(method_name)
    if func is None:
        return JsonResponse({"status": "error"}, status=400)

    result = func(request, request_body)
    return result


def save_selected_columns(request, request_body):
    try:
        selected_columns = request_body.get("columns", [])

        # Save or update the selected columns for the user
        selected_columns_record, created = SelectedColumns.objects.get_or_create(
            user=request.user
        )
        selected_columns_record.columns = json.dumps(selected_columns)
        selected_columns_record.save()

        return JsonResponse({"status": "success", "message": selected_columns})

    except:
        return JsonResponse({"status": "error"})
