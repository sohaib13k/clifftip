from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Report
from unittest.mock import patch


class ViewReportTests(TestCase):
    def setUp(self):
        # Set up a user and log them in
        self.user = get_user_model().objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        self.report = Report.objects.create(
            id=1, name="All Parties", is_masterdata=True
        )

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse("report-view", args=(self.report.id,)))
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_report_not_found(self):
        response = self.client.get(
            reverse("report-view", args=(999,))
        )  # Assuming 999 does not exist
        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid report id passed.", response.content.decode())

    @patch("report.models.Report.objects.get")
    def test_multiple_reports_found(self, mock_get):
        mock_get.side_effect = Report.MultipleObjectsReturned
        self.report.access_users.add(self.user)
        response = self.client.get(reverse("report-view", args=(1,)))
        self.assertIn("Multiple reports found", response.content.decode())

    def test_authorisation(self):
        response = self.client.get(reverse("report-view", args=(1,)))
        self.assertIn("Invalid report id passed.", response.content.decode())