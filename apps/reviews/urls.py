from django.urls import path

from apps.reviews.views import (
    ApproveApplicationView,
    ApplicationReviewView,
    DecisionHistoryView,
    OfficerQueueView,
    RejectApplicationView,
    RequestMoreInfoView,
)

app_name = "reviews"

urlpatterns = [
    path("queue/", OfficerQueueView.as_view(), name="queue"),
    path("history/", DecisionHistoryView.as_view(), name="history"),
    path("<uuid:pk>/", ApplicationReviewView.as_view(), name="review"),
    path("<uuid:pk>/approve/", ApproveApplicationView.as_view(), name="approve"),
    path("<uuid:pk>/reject/", RejectApplicationView.as_view(), name="reject"),
    path("<uuid:pk>/request-info/", RequestMoreInfoView.as_view(), name="request_info"),
]
