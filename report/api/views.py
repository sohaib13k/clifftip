from django.http import JsonResponse
from django.views import View
from report.models import Report
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from commonutil import commonutil
import json
import os
import pandas as pd


class ReportView(LoginRequiredMixin, View):

    login_url = "/account/login/"
    redirect_field_name = "next"  # This field can be used to redirect back to to the original page after login

    def get(self, request, report_id=None):
        report = request.user.accessible_reports_users.get(id=report_id)

        if report.is_masterdata:
            return JsonResponse(
                {"error": "Masterdata cannot be filtered, since date column missing."},
                status=406,
            )

        interval = request.GET.get("interval")

        if interval:
            if interval not in ["day", "week", "month", "year"]:
                return JsonResponse({"error": "Invalid interval provided."}, status=400)
            start_date, end_date = commonutil.get_interval_date_str(interval)

        else:
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            if not start_date or not end_date:
                return JsonResponse(
                    {
                        "error": "Start date and end date required when interval is not provided."
                    },
                    status=400,
                )
        # start_date = "2024-05-01"
        start_year_month = tuple(map(int, start_date.split("-")[:2]))  # (year, month)
        end_year_month = tuple(map(int, end_date.split("-")[:2]))  # (year, month)

        csv_directory = settings.CSV_DIR / report.service_name

        agg_data = pd.DataFrame()

        try:
            for filename in os.listdir(csv_directory):
                if filename.endswith(".csv"):
                    # Remove ".csv" extension
                    file_year_month = tuple(map(int, filename[:-4].split("_")[:2]))

                    if start_year_month <= file_year_month <= end_year_month:
                        file_path = os.path.join(csv_directory, filename)
                        df = pd.read_csv(file_path)
                        agg_data = pd.concat([agg_data, df], ignore_index=True)

        except FileNotFoundError:
            return JsonResponse(data={}, status=204)

        filtered_data = pd.DataFrame()

        if not agg_data.empty:
            filtered_data = agg_data[
                (agg_data[report.date_col] >= start_date)
                & (agg_data[report.date_col] <= end_date)
            ]

        if not filtered_data.empty:
            result = filtered_data.sort_values(report.date_col).to_json(
                orient="records"
            )
        else:
            result = "[]"

        return JsonResponse(
            result,
            safe=False,
        )

    # def post(self, request):
    #     # Create a new report
    #     try:
    #         data = json.loads(request.body)
    #         report = Report.objects.create(
    #             name=data["name"],
    #             # Set other fields from data
    #         )
    #         return JsonResponse(
    #             {"message": "Report created", "report_id": report.id}, status=201
    #         )
    #     except (KeyError, TypeError):
    #         return JsonResponse({"error": "Invalid data"}, status=400)

    # def put(self, request, report_id=None):
    #     # Update an existing report
    #     if not report_id:
    #         return JsonResponse(
    #             {"error": "Method PUT requires a report ID"}, status=400
    #         )
    #     try:
    #         data = json.loads(request.body)
    #         report = Report.objects.get(id=report_id)
    #         report.name = data["name"]
    #         # Update other fields from data
    #         report.save()
    #         return JsonResponse({"message": "Report updated"}, status=200)
    #     except Report.DoesNotExist:
    #         return JsonResponse({"error": "Report not found"}, status=404)
    #     except KeyError:
    #         return JsonResponse({"error": "Invalid data"}, status=400)

    # def delete(self, request, report_id=None):
    #     # Delete a report
    #     if not report_id:
    #         return JsonResponse(
    #             {"error": "Method DELETE requires a report ID"}, status=400
    #         )
    #     try:
    #         report = Report.objects.get(id=report_id)
    #         report.delete()
    #         return JsonResponse({"message": "Report deleted"}, status=200)
    #     except Report.DoesNotExist:
    #         return JsonResponse({"error": "Report not found"}, status=404)
