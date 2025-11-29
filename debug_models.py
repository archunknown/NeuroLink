import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    print(f"Listing models using key: {api_key[:5]}...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("\n--- Available Models ---")
        for model in data.get("models", []):
            name = model.get("name")
            supported_methods = model.get("supportedGenerationMethods", [])
            if "generateContent" in supported_methods:
                print(f"Name: {name}")
                print(f"  Methods: {supported_methods}")
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
