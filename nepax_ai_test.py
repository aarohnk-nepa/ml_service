import httpx
import os

BASE = os.environ['NEPAX_GATEWAY_URL']

HEADERS = {
    "X-Tenant-ID": os.environ["NEPAX_TENANT_ID"],
    "X-API-Key": os.environ["NEPAX_API_KEY"],
    "X-Nepax-Module": "ml-service",
}

def chat(prompt: str, model: str = 'gpt-4o-mini', **kwargs) -> str:
    r = httpx.post(
        f"{BASE}/chat/completions",
        headers=HEADERS,
        json={"model": model, "messages": [{"role": "user", "content": prompt}], **kwargs},
        timeout=60,
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

print(chat("reply with a single word: gng", max_tokens=5, temperature=0))
