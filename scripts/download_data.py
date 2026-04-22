import os
import requests

DATA_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
OUTPUT_PATH = "sample.csv"

os.makedirs(".", exist_ok=True)

r = requests.get(DATA_URL)
r.raise_for_status()

with open(OUTPUT_PATH, "wb") as f:
    f.write(r.content)

print("✅ Dataset downloaded")