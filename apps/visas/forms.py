from django import forms

from apps.visas.models import InterviewSchedule, VisaType


class VisaTypeForm(forms.ModelForm):
    class Meta:
        model = VisaType
        fields = ["code", "name", "description", "fee_amount", "max_stay_days", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "e.g. TOURIST"}),
            "name": forms.TextInput(attrs={"placeholder": "e.g. Tourist Visa"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "fee_amount": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "max_stay_days": forms.NumberInput(attrs={"min": "1"}),
        }


class InterviewScheduleForm(forms.Form):

    interview_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        label="Interview Date & Time",
    )
    google_meet_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://meet.google.com/..."}),
        label="Google Meet Link",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Additional notes for the applicant…"}),
        label="Notes",
    )
