from django.http import JsonResponse
from django.views import View
from report.models import Report
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import os
import datetime
import pandas as pd


class ReportView(LoginRequiredMixin, View):

    login_url = "/account/login/"
    redirect_field_name = "next"  # This field can be used to redirect back to to the original page after login

    def get(self, request, report_id=None):
        print(report_id)
        report = request.user.accessible_reports_users.get(id=report_id)

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        start_year_month = tuple(map(int, start_date.split("-")[:2]))  # (year, month)
        end_year_month = tuple(map(int, end_date.split("-")[:2]))  # (year, month)

        csv_directory = settings.CSV_DIR / report.name

        agg_data = pd.DataFrame()

        for filename in os.listdir(csv_directory):
            if filename.endswith(".csv"):
                # Remove ".csv" extension
                file_year_month = tuple(map(int, filename[:-4].split("_")[:2]))

                if (
                    start_year_month is None or start_year_month <= file_year_month
                ) and (end_year_month is None or end_year_month >= file_year_month):
                    file_path = os.path.join(csv_directory, filename)
                    df = pd.read_csv(file_path)
                    agg_data = pd.concat([agg_data, df], ignore_index=True)

        return JsonResponse(agg_data.to_json(orient="records"), safe=False)

    def post(self, request):
        # Create a new report
        try:
            data = json.loads(request.body)
            report = Report.objects.create(
                name=data["name"],
                # Set other fields from data
            )
            return JsonResponse(
                {"message": "Report created", "report_id": report.id}, status=201
            )
        except (KeyError, TypeError):
            return JsonResponse({"error": "Invalid data"}, status=400)

    def put(self, request, report_id=None):
        # Update an existing report
        if not report_id:
            return JsonResponse(
                {"error": "Method PUT requires a report ID"}, status=400
            )
        try:
            data = json.loads(request.body)
            report = Report.objects.get(id=report_id)
            report.name = data["name"]
            # Update other fields from data
            report.save()
            return JsonResponse({"message": "Report updated"}, status=200)
        except Report.DoesNotExist:
            return JsonResponse({"error": "Report not found"}, status=404)
        except KeyError:
            return JsonResponse({"error": "Invalid data"}, status=400)

    def delete(self, request, report_id=None):
        # Delete a report
        if not report_id:
            return JsonResponse(
                {"error": "Method DELETE requires a report ID"}, status=400
            )
        try:
            report = Report.objects.get(id=report_id)
            report.delete()
            return JsonResponse({"message": "Report deleted"}, status=200)
        except Report.DoesNotExist:
            return JsonResponse({"error": "Report not found"}, status=404)
