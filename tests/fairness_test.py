import requests
import time
import os
import sys

API_URL = "http://127.0.0.1:8000/bias/analyze-dataset?response_mode=full"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "sample.csv")

FAILED = False

# Wait for API
for i in range(10):
    try:
        requests.get("http://127.0.0.1:8000/docs")
        print("API is up")
        break
    except:
        print("Waiting for API...")
        time.sleep(2)
else:
    print("API did not start")
    sys.exit(1)

# Call API
with open(DATASET_PATH, "rb") as f:
    response = requests.post(API_URL, files={"file": f})

if response.status_code != 200:
    print("API Error:", response.text)
    sys.exit(1)

result = response.json()

print("\nFULL RESPONSE:\n", result)

bias_results = result.get("preliminary_bias_signals")

if not bias_results:
    print("No fairness signals returned")
    sys.exit(1)

for attr, metrics in bias_results.items():
    ratio = metrics.get("disparate_impact_ratio")

    if ratio is None:
        continue

    print(f"{attr} -> {ratio}")

    if ratio < 0.8:
        print(f"BIAS DETECTED in {attr}")
        FAILED = True

if FAILED:
    sys.exit(1)

print("\nFAIRNESS TEST PASSED")