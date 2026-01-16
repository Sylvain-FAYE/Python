API_KEY = "AIzaSyCZLwrpH2lfQw4I-1dbNZ2zrnGPX1xTtM8"

import os
import json
import time
import math
import requests
import rich.console

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

OUTFILE = "restaurants_dakar.json"

CENTER_LAT = 14.6928
CENTER_LNG = -17.4467
RADIUS_M = 5000
KEYWORD = "restaurant"

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# ---------------------------
# Google Places
# ---------------------------
def fetch_page(pagetoken=None):
    params = {
        "key": API_KEY,
        "location": f"{CENTER_LAT},{CENTER_LNG}",
        "radius": RADIUS_M,
        "keyword": KEYWORD,
        "type": "restaurant",
    }
    if pagetoken:
        params["pagetoken"] = pagetoken

    r = requests.get(PLACES_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all(max_pages=3):
    if not API_KEY:
        raise SystemExit("Missing GOOGLE_MAPS_API_KEY")

    all_results = []
    token = None

    for _ in range(max_pages):
        data = fetch_page(token)
        results = data.get("results", [])
        all_results.extend(results)

        token = data.get("next_page_token")
        if not token:
            break

        time.sleep(2.2)

    return all_results


# ---------------------------
# Helpers
# ---------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def get_loc(place):
    loc = place.get("geometry", {}).get("location", {})
    return loc.get("lat"), loc.get("lng")


# ---------------------------
# Filtering
# ---------------------------
def filter_places(places, min_rating, min_reviews, max_price, keyword, open_now):
    rows = []
    keyword = keyword.lower()

    for p in places:
        name = p.get("name", "")
        rating = p.get("rating")
        reviews = p.get("user_ratings_total", 0)
        price = p.get("price_level")
        lat, lng = get_loc(p)
        open_flag = p.get("opening_hours", {}).get("open_now")

        if rating is None or lat is None or lng is None:
            continue
        if rating < min_rating:
            continue
        if reviews < min_reviews:
            continue
        if max_price is not None and price is not None and price > max_price:
            continue
        if keyword and keyword not in name.lower():
            continue
        if open_now is not None and open_flag != open_now:
            continue

        dist = haversine_km(CENTER_LAT, CENTER_LNG, lat, lng)

        rows.append({
            "name": name,
            "rating": rating,
            "reviews": reviews,
            "price": price,
            "distance": dist,
            "open": open_flag,
            "address": p.get("vicinity")
        })

    rows.sort(key=lambda r: (-r["rating"], -r["reviews"], r["distance"]))
    return rows


# ---------------------------
# Rich table output
# ---------------------------
def print_table(rows, limit=20):
    table = Table(title="🍽️ Dakar Restaurants", header_style="bold cyan")

    table.add_column("Name", style="bold", width=32)
    table.add_column("Rating", justify="right")
    table.add_column("Reviews", justify="right")
    table.add_column("Price", justify="center")
    table.add_column("Km", justify="right")
    table.add_column("Open", justify="center")

    for r in rows[:limit]:
        table.add_row(
            r["name"][:30],
            f'{r["rating"]:.1f}',
            str(r["reviews"]),
            str(r["price"] if r["price"] is not None else "-"),
            f'{r["distance"]:.2f}',
            "✓" if r["open"] else "-"
        )

    console.print(table)


# ---------------------------
# Main
# ---------------------------
def main():
    console.rule("[bold]Fetching restaurants from Google Places")
    places = fetch_all()
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    console.print(f"[green]Saved {len(places)} restaurants to {OUTFILE}[/green]")

    while True:
        console.rule("[bold]Filter restaurants")

        min_rating = float(Prompt.ask("Minimum rating", default="4.0"))
        min_reviews = int(Prompt.ask("Minimum reviews", default="50"))
        mp = Prompt.ask("Max price level (0–4, blank = ignore)", default="")
        max_price = int(mp) if mp else None
        keyword = Prompt.ask("Keyword (pizza, seafood, blank = none)", default="")
        open_now = Confirm.ask("Only show open restaurants?", default=False)

        rows = filter_places(
            places,
            min_rating=min_rating,
            min_reviews=min_reviews,
            max_price=max_price,
            keyword=keyword,
            open_now=open_now,
        )

        console.print(f"\n[bold]{len(rows)} restaurants found[/bold]\n")
        print_table(rows)

        if not Confirm.ask("\nAnother search?", default=True):
            break

    console.print("\n[bold green]Done.[/bold green]")


if __name__ == "__main__":
    main()