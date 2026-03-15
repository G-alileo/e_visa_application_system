import uuid

from django import forms

from apps.applications.models import VisaApplication
from apps.visas.models import VisaType


class CreateApplicationForm(forms.ModelForm):
    class Meta:
        model = VisaApplication
        fields = [
            "visa_type",
            "nationality",
            "purpose_of_travel",
            "intended_entry_date",
            "full_name",
            "date_of_birth",
            "gender",
            "passport_number",
            "passport_expiry",
        ]
        widgets = {
            "visa_type": forms.Select(attrs={"class": "form-select"}),
            "nationality": forms.TextInput(attrs={"placeholder": "e.g. NG", "maxlength": 2}),
            "purpose_of_travel": forms.TextInput(attrs={"placeholder": "e.g. Tourism, Business"}),
            "intended_entry_date": forms.DateInput(attrs={"type": "date"}),
            "full_name": forms.TextInput(attrs={"placeholder": "As shown on passport"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "gender": forms.TextInput(attrs={"placeholder": "e.g. Male, Female"}),
            "passport_number": forms.TextInput(attrs={"placeholder": "Passport number"}),
            "passport_expiry": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["visa_type"].queryset = VisaType.objects.filter(is_active=True).order_by("name")
        self.fields["nationality"].label = "Nationality (ISO 2-letter code)"
        self.fields["full_name"].required = True
        self.fields["date_of_birth"].required = True
        self.fields["gender"].required = True
        self.fields["passport_number"].required = True
        self.fields["passport_expiry"].required = True

    def clean_nationality(self):
        return (self.cleaned_data.get("nationality") or "").strip().upper()
