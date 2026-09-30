"""Milestone 0 scratch test: confirm Ollama + llama3.2:3b respond."""
import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Say hello in 5 words"}],
)
print(response["message"]["content"])
