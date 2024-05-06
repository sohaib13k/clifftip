from django import forms
from django.core.exceptions import ValidationError
from .models import Report
import re


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data.get("name")
        # Regex to check for alphanumeric characters with only one in-between space
        if not re.match(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$", name):
            raise ValidationError(
                "Name must be alphanumeric and may contain only one in-between space."
            )
        return name

    def clean_time_col(self):
        is_datetime_merged = self.cleaned_data.get("is_datetime_merged")
        date_col = self.cleaned_data.get("date_col")
        time_col = self.cleaned_data.get("time_col")

        if is_datetime_merged and date_col != time_col:
            raise ValidationError(
                'If "Same column for date & time" is selected, then both date and time values should be the same.'
            )
        return time_col

    def clean(self):
        cleaned_data = super().clean()
        is_custom_report = cleaned_data.get('is_custom_report')
        reports = cleaned_data.get('reports')

        if not is_custom_report and reports.exists():
            raise ValidationError(
                {
                    "is_custom_report": "Kindly select this checkbox if this is a customised report",
                    "reports": 'Kindly check the "Customised Report" checkbox, if report to be associated. \
                        Otherwise remove all selection from right side box.',
                }
            )

        if is_custom_report and not reports.exists():
            raise ValidationError({
                'reports': "Kindly add reports, otherwise uncheck \"Customised Report\"."
            })

        if is_custom_report and len(reports)<=1:
            raise ValidationError({
                'reports': "Minumum two reports should be added."
            })

        # Additional check for date_col or is_masterdata
        date_col = cleaned_data.get("date_col")
        is_masterdata = cleaned_data.get("is_masterdata")

        if not (date_col or is_masterdata):
            errors = {}
            if not date_col:
                errors['date_col'] = "This field is required unless 'Master data sheet' is checked."
            if not is_masterdata:
                errors['is_masterdata'] = "This field must be checked unless a 'Date column header' is provided."
            raise ValidationError(errors)

        return cleaned_data
