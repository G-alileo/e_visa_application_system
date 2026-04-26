from django.urls import path

from apps.chatbot.views import ChatbotMessageView

app_name = "chatbot"

urlpatterns = [
    path("message/", ChatbotMessageView.as_view(), name="message"),
]
