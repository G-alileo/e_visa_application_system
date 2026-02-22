from django import forms

from apps.visas.models import VisaType


class VisaTypeForm(forms.ModelForm):
    class Meta:
        model = VisaType
        fields = ["code", "name", "description", "fee_amount", "max_stay_days", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "e.g. TOURIST_30"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g. Tourist Visa (30 days)"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "fee_amount": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "max_stay_days": forms.NumberInput(attrs={"min": "1"}),
        }
