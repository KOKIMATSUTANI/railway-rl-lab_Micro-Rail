import requests
import json
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

print(Path(__file__).resolve())
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

## dresden_latest_10.07.(successued in ingestion)
query = """

[out:json][timeout:60];

way
  ["railway"="rail"]
  ["railway:traffic_mode"="passenger"]
(
  51.028345784002994,
  13.680787971237923,
  51.08500227968741,
  13.751385844266505
);

(._;>;);

out body;
"""

headers = {
    "User-Agent": "KokiRailwayProject/1.0"
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36(Research Project: datadriven-dispatch; contact: info@example.com)"  
}

response = requests.post(
    OVERPASS_URL,
    data=query,
    headers=headers,
    timeout=120
)

response.raise_for_status()

data = response.json()



with open(DATA_DIR / "dresden_railway_ver20260710.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(data['elements'])} objects saved.")