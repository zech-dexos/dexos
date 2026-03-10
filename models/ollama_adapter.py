import requests
from .base_adapter import BaseAdapter


class OllamaAdapter(BaseAdapter):

    def __init__(self, model="llama3.1:8b-instruct-q6_K"):
        self.model = model
        self.host = "http://localhost:11434"

    def generate(self, prompt, system=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        if system:
            payload["system"] = system

        r = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=120
        )
        r.raise_for_status()

        data = r.json()

        if "response" not in data:
            raise RuntimeError(f"Ollama returned unexpected payload: {data}")

        return data["response"].strip()

    def health_check(self):
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=10)
            return r.status_code == 200
        except Exception:
            return False

    def model_name(self):
        return self.model


if __name__ == "__main__":
    adapter = OllamaAdapter()

    print("DexOS Model Adapter Test")
    print("------------------------")
    print("Health:", adapter.health_check())
    print("Model:", adapter.model_name())

    if adapter.health_check():
        try:
            result = adapter.generate("Say hello from DexOS in one short sentence.")
            print("\nSample Generation:")
            print(result if result else "[EMPTY RESPONSE]")
        except Exception as e:
            print("\nGeneration Error:")
            print(e)
