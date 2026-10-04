import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Load the backend's .env file.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

MODEL_NAME = "gemma-4-26b-a4b-it"


class AIProviderError(RuntimeError):
    """Raised when the AI provider request fails."""


class AIProviderTimeoutError(AIProviderError):
    """Raised when the AI provider request times out."""


def get_ai_response(prompt: str) -> str:
    """Send a prompt to Gemma and return its response."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
        raise AIProviderError("GEMINI_API_KEY is not configured.")

    try:
        client = genai.Client(
            api_key=api_key,
            http_options={"timeout": 120_000},
        )

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            answer = response.text

            if not answer or not answer.strip():
                raise AIProviderError(
                    "Gemma returned an empty response."
                )

            return answer.strip()

        finally:
            client.close()

    except AIProviderError:
        raise

    except Exception as exc:
        error_name = type(exc).__name__
        error_message = str(exc)

        print(
            f"Gemma request failed: {error_name}: "
            f"{error_message}"
        )

        if "timeout" in error_name.lower() or "timed out" in error_message.lower():
            raise AIProviderTimeoutError(
                "Gemma took too long to respond. Please try again."
            ) from exc

        raise AIProviderError(
            "Gemma could not complete the request. "
            "Check the backend terminal for the provider error."
        ) from exc
