import requests
import sys

OLLAMA_HOST = "http://127.0.0.1:11434"

print(f"Attempting to connect to {OLLAMA_HOST}...")

try:
    resp = requests.get(f"{OLLAMA_HOST}/", timeout=2.0)
    print(f"Status Code: {resp.status_code}")
    print(f"Response Text: {resp.text}")
    if resp.status_code == 200:
        print("SUCCESS: Ollama is reachable.")
    else:
        print("FAILURE: Ollama returned non-200 status.")
except Exception as e:
    print(f"ERROR: Exception occurred: {e}")
    sys.exit(1)
