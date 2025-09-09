# ingest/ingest_us_data.py

import subprocess
import sys
from pathlib import Path

# === CONFIGURATION ===

# Change this to your actual Google Drive path
GDRIVE_ROOT = Path("X:/QuantumTickAI/trading-lab")
TARGET_DIR = GDRIVE_ROOT / "data" / "raw" / "us_data"
GET_DATA_SCRIPT = Path(__file__).parent / "qlib" / "scripts" / "get_data.py"

def download_us_data():
    print(f"📥 Downloading US QLib data to: {TARGET_DIR}")

    cmd = [
        sys.executable,
        str(GET_DATA_SCRIPT),
        "qlib_data",
        "--target_dir", str(TARGET_DIR),
        "--region", "us"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ US dataset downloaded successfully.")
    else:
        print("❌ Error occurred:")
        print(result.stdout)
        print(result.stderr)

if __name__ == "__main__":
    download_us_data()
