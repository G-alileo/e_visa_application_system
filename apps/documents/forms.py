from django import forms

from apps.documents.choices import DocumentType
from apps.documents.models import ApplicationDocument


class DocumentUploadForm(forms.Form):
    document_type = forms.ChoiceField(choices=DocumentType.choices)
    file = forms.FileField(
        help_text="Upload a PDF, JPG, or PNG (max 5 MB).",
        widget=forms.FileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )
