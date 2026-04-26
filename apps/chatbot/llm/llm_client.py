import json
import os
import urllib.error
import urllib.request


class LLMClient:
    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or os.getenv("LLM_MODEL", "gemini-1.5-flash")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self._temperature = float(os.getenv("CHATBOT_TEMPERATURE", "0.2"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_answer(self, question: str, contexts: list[str]) -> str:
        if not contexts:
            return (
                "I could not find relevant information in the current knowledge base for that question. "
                "Please rephrase your question or update the knowledge base content."
            )

        if not self.is_configured:
            return self._fallback_answer(contexts)

        prompt = self._build_prompt(question=question, contexts=contexts)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self._temperature,
                "maxOutputTokens": 512,
            },
        }
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"LLM request failed with status {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach LLM service: {exc.reason}") from exc

        candidates = response_payload.get("candidates", [])
        if not candidates:
            raise RuntimeError("LLM returned no candidates for the prompt.")
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "".join(part.get("text", "") for part in parts).strip()
        if not answer:
            raise RuntimeError("LLM response did not contain text output.")
        return answer

    def _build_prompt(self, *, question: str, contexts: list[str]) -> str:
        context_sections = [
            f"[Context {index + 1}]\n{context.strip()}"
            for index, context in enumerate(contexts)
        ]
        context_blob = "\n\n".join(context_sections)
        return (
            "You are the official E-Visa assistant for this application.\n"
            "Answer ONLY using the provided context.\n"
            "If the context is not enough, clearly say you do not have enough information.\n"
            "Be concise, accurate, and practical for applicants.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Knowledge base context:\n{context_blob}"
        )

    def _fallback_answer(self, contexts: list[str]) -> str:
        top_context = contexts[0].strip()
        excerpt = top_context[:600]
        return (
            "Chat model is not configured (set GEMINI_API_KEY in your environment). "
            "Here is the most relevant information from the knowledge base:\n\n"
            f"{excerpt}"
        )
