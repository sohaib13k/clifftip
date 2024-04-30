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
        if not re.match(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)?$", name):
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
