from django import forms


class DecisionReasonForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Written justification for this decision..."}),
        max_length=2000,
    )


class RequestInfoForm(forms.Form):
    note = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Describe what additional information is needed..."}),
        max_length=2000,
        label="Information requested",
    )
