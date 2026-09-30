"""Ollama wrapper with friendly error handling."""
import ollama

DEFAULT_MODEL = "llama3.2:3b"


class LLMError(Exception):
    """Raised with a user-friendly message when the local model can't be used."""


def ask_llm(prompt: str, model: str = DEFAULT_MODEL, timeout: float = 120.0) -> str:
    try:
        client = ollama.Client(timeout=timeout)
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2},
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        if getattr(e, "status_code", None) == 404:
            raise LLMError(f"Model '{model}' not found. Run: ollama pull {model}") from e
        raise LLMError(f"The model returned an error: {e}") from e
    except ConnectionError as e:
        raise LLMError("Could not reach Ollama. Make sure the Ollama app is running.") from e
    except Exception as e:
        raise LLMError(f"Could not get a response from the local model ({type(e).__name__}).") from e
