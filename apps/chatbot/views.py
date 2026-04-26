import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from apps.chatbot.rag import get_rag_chatbot


@method_decorator(require_POST, name="dispatch")
class ChatbotMessageView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        message = str(payload.get("message", "")).strip()
        if not message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        if len(message) > 4000:
            return JsonResponse({"error": "Message is too long."}, status=400)

        try:
            result = get_rag_chatbot().ask(message)
        except RuntimeError as exc:
            return JsonResponse({"error": str(exc)}, status=503)

        return JsonResponse(
            {
                "answer": result.answer,
            }
        )
