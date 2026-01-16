import os
import time
import json
import requests
import pandas as pd

OUTFILE_JSON = "restaurants_dakar_full.json"
OUTFILE_XLSX = "restaurants_dakar.xlsx"

CENTER_LAT = 14.675348733894099
CENTER_LON = -17.433205056641178
RADIUS_M = 5000
KEYWORD = "restaurant"
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

API_KEY = "AIzaSyCcRPVqS_dMQUqfztNsVAdGIJZ56Ki1QEY"


def fetch_page(page_token=None):
    params = {
        "location": f"{CENTER_LAT},{CENTER_LON}",
        "radius": RADIUS_M,
        "keyword": KEYWORD,
        "key": API_KEY,
    }
    if page_token:
        params["pagetoken"] = page_token

    r = requests.get(PLACES_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all_results(max_pages=20):
    all_results = []
    token = None

    for _ in range(max_pages):
        data = fetch_page(token)

        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Google Places error: status={status}, info={data.get('error_message')}")

        all_results.extend(data.get("results", []))

        token = data.get("next_page_token")
        if not token:
            break

        # Important: Google demande souvent d'attendre un peu avant que le token devienne valide
        time.sleep(2.2)

    return all_results


def flatten_place(p):
    loc = (p.get("geometry") or {}).get("location") or {}
    opening = p.get("opening_hours") or {}
    return {
        "place_id": p.get("place_id"),
        "name": p.get("name"),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "vicinity": p.get("vicinity"),
        "business_status": p.get("business_status"),
        "open_now": opening.get("open_now"),
        "rating": p.get("rating"),
        "user_ratings_total": p.get("user_ratings_total"),
        "price_level": p.get("price_level"),
        "types": ", ".join(p.get("types", [])),
        "phone_in_payload": p.get("international_phone_number") or p.get("formatted_phone_number"),
    }


def main():
    results = fetch_all_results(max_pages=20)

    # Sauvegarde JSON complet (optionnel mais pratique)
    with open(OUTFILE_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    rows = [flatten_place(p) for p in results]
    df = pd.DataFrame(rows).drop_duplicates(subset=["place_id"])

    # Excel
    df.to_excel(OUTFILE_XLSX, index=False)

    print(f"✅ {len(df)} restaurants exportés vers: {OUTFILE_XLSX}")
    print(f"✅ JSON complet: {OUTFILE_JSON}")


if __name__ == "__main__":
    main()