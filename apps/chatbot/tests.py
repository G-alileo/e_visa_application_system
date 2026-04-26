import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.chatbot.rag import ChatbotResult


class ChatbotMessageViewTests(TestCase):
    def test_message_endpoint_rejects_invalid_json(self):
        response = self.client.post(
            reverse("chatbot:message"),
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON payload.")

    def test_message_endpoint_rejects_empty_message(self):
        response = self.client.post(
            reverse("chatbot:message"),
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Message cannot be empty.")

    @patch("apps.chatbot.views.get_rag_chatbot")
    def test_message_endpoint_returns_answer(self, mock_get_rag_chatbot):
        mock_get_rag_chatbot.return_value.ask.return_value = ChatbotResult(
            answer="Sample answer",
            sources=[{"chunk_index": 0, "score": 0.93, "excerpt": "Sample excerpt"}],
        )

        response = self.client.post(
            reverse("chatbot:message"),
            data=json.dumps({"message": "What visa options do I have?"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Sample answer")
        self.assertNotIn("sources", response.json())
