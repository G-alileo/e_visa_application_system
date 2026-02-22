from django.urls import path

from apps.payments.views import PaymentView

app_name = "payments"

urlpatterns = [
    path("<uuid:pk>/", PaymentView.as_view(), name="payment"),
]
