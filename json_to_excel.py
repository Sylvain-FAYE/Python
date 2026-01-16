import json
import math
import pandas as pd

INFILE = "restaurants_dakar.json"
OUTFILE = "restaurants_dakar.xlsx"

# Same reference point used in the main script
CENTER_LAT = 14.6928
CENTER_LNG = -17.4467


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def main():
    with open(INFILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for r in data:
        name = r.get("name")
        rating = r.get("rating")
        reviews = r.get("user_ratings_total")
        price = r.get("price_level")
        open_now = r.get("opening_hours", {}).get("open_now")
        address = r.get("vicinity") or r.get("formatted_address")

        loc = r.get("geometry", {}).get("location", {})
        lat = loc.get("lat")
        lng = loc.get("lng")

        if lat is not None and lng is not None:
            distance_km = haversine_km(CENTER_LAT, CENTER_LNG, lat, lng)
        else:
            distance_km = None

        rows.append({
            "name": name,
            "rating": rating,
            "reviews": reviews,
            "price_level": price,
            "open_now": open_now,
            "distance_km": distance_km,
            "address": address,
            "lat": lat,
            "lng": lng,
        })

    df = pd.DataFrame(rows)

    # Optional: nicer ordering of columns
    df = df[
        [
            "name",
            "rating",
            "reviews",
            "price_level",
            "open_now",
            "distance_km",
            "address",
            "lat",
            "lng",
        ]
    ]

    df.to_excel(OUTFILE, index=False)
    print(f"Saved {len(df)} rows to {OUTFILE}")


if __name__ == "__main__":
    main()