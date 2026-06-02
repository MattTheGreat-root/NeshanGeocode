import pandas as pd
import requests
import json
import time
import os

# ------------------ CONFIGURATION ------------------
API_KEY = "YOUR_API"                
INPUT_FILE = "postal_filtered.xlsx"              
ADDRESS_COLUMN = "address"              
OUTPUT_FILE = "geocoded_progress.xlsx"  
REQUEST_DELAY = 0.3                     
CLEAN_ADDRESS = True                   
# ---------------------------------------------------

def clean_address(raw_address: str) -> str:
    """Convert hyphen-separated address into a natural Persian address."""
    if not isinstance(raw_address, str):
        return raw_address
    cleaned = raw_address.strip()
    if not cleaned:
        return cleaned
    # Preproccessing
    cleaned = cleaned.replace('-', '، ')
    cleaned = cleaned.rstrip('، ')
    return cleaned

def geocode_address(address: str, api_key: str) -> dict:
    """
    Send one address to the Neshan Geocoding API.
    Returns dict with latitude, longitude, status, error_message.
    """
    base_url = "https://api.neshan.org/geocoding/v1/plus"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {"address": address}
    params = {"json": json.dumps(payload, ensure_ascii=False)}
    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                loc = items[0].get("location", {})
                return {"latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                        "status": "success",
                        "error_message": ""}
            else:
                return {"latitude": None, "longitude": None,
                        "status": "no_result",
                        "error_message": "No matching location found."}
        else:
            return {"latitude": None, "longitude": None,
                    "status": f"HTTP {resp.status_code}",
                    "error_message": resp.text}
    except Exception as e:
        return {"latitude": None, "longitude": None,
                "status": "exception",
                "error_message": str(e)}

def main():
    # 1. Load the original input data
    df_input = pd.read_excel(INPUT_FILE)
    total = len(df_input)
    print(f"Loaded {total} addresses from '{INPUT_FILE}'.")

    if ADDRESS_COLUMN not in df_input.columns:
        raise ValueError(f"Column '{ADDRESS_COLUMN}' not found. Available: {list(df_input.columns)}")

    # 2. Check if a progress file exists
    if os.path.exists(OUTPUT_FILE):
        print(f"Progress file '{OUTPUT_FILE}' found. Loading previous progress...")
        df = pd.read_excel(OUTPUT_FILE)
        for col in ["latitude", "longitude", "geocode_status", "geocode_error", "processed"]:
            if col not in df.columns:
                df[col] = None if col != "processed" else False
        processed_mask = df.get("processed", pd.Series([False]*len(df))).astype(bool)
        remaining = (~processed_mask).sum()
        print(f"Already processed: {processed_mask.sum()}, still to do: {remaining}")
    else:
        print("No progress file found. Starting fresh.")
        df = df_input.copy()
        df["latitude"] = None
        df["longitude"] = None
        df["geocode_status"] = None
        df["geocode_error"] = None
        df["processed"] = False
        remaining = total

    if remaining == 0:
        print("All addresses already processed. Nothing to do.")
        return

    # 3. Process addresses that haven't been done yet
    for idx, row in df.iterrows():
        if row.get("processed", False):
            continue

        original_address = str(row[ADDRESS_COLUMN]).strip()
        # Optionally clean the address before sending
        address_to_send = clean_address(original_address) if CLEAN_ADDRESS else original_address

        progress_idx = list(df.index).index(idx) + 1
        print(f"\n[{progress_idx}/{total}] Geocoding: {address_to_send}")

        result = geocode_address(address_to_send, API_KEY)

        df.at[idx, "latitude"] = result["latitude"]
        df.at[idx, "longitude"] = result["longitude"]
        df.at[idx, "geocode_status"] = result["status"]
        df.at[idx, "geocode_error"] = result["error_message"]
        df.at[idx, "processed"] = True

        print(f"  -> {result['status']}: lat={result['latitude']}, lng={result['longitude']}")
        if result["error_message"]:
            print(f"     Error: {result['error_message']}")

        # Save after each address
        df.to_excel(OUTPUT_FILE, index=False)
        time.sleep(REQUEST_DELAY)

    print(f"\nAll addresses processed. Final results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()