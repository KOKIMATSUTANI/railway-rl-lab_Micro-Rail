import json 
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILENAME = "dresden_railway_ver20260710.json"

with open(DATA_DIR / FILENAME, encoding="utf-8") as f:
    osm = json.load(f)

print(f"Loaded {len(osm['elements'])} objects from {FILENAME}.")
# for i, p in enumerate(Path(__file__).resolve().parents):
#     print(i, p)