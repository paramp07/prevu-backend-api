import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Access environment variables
CSE_ID = os.environ["CSE_ID"]
API_KEY = os.environ["API_KEY"]

BAD_DOMAINS = [
    "lookaside.fbsbx.com",
    "lookaside.instagram.com",
    "tiktok.com"
]

def fetch_image_links(query: str, num_images: int = 6) -> list:
    """Fetch image URLs from Google Custom Search for a given query, excluding known bad domains."""
    exclusions = " ".join(f"-site:{domain}" for domain in BAD_DOMAINS)
    full_query = f"{query} {exclusions}"

    url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"q={full_query}&num={num_images}&start=1&imgSize=huge&searchType=image&"
        f"key={API_KEY}&cx={CSE_ID}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [item["link"] for item in data.get("items", [])]
    except Exception as e:
        print(f"❌ Error fetching images for '{query}': {e}")
        return []

def enrich_menu_with_images(menu_data: dict) -> dict:
    restaurant = menu_data.get("restaurant_name", "")
    location = menu_data.get("location", "")

    # 🏞️ Add a restaurant-level image
    if restaurant:
        restaurant_query = f"{restaurant} restaurant {location}".strip()
        print(f"🏞️ Fetching top-level restaurant image for: {restaurant_query}")
        images = fetch_image_links(restaurant_query)
        menu_data["restaurant_image"] = images[0] if images else ""
    else:
        print("⚠️ No restaurant name found; skipping top-level image.")
        menu_data["restaurant_image"] = ""

    # 🖼️ Add images for each dish
    for category in menu_data.get("menu", []):
        for item in category.get("items", []):
            name = item.get("name", "")
            desc = item.get("description", "")
            query = f"{name} - {desc} - {restaurant}".strip(" -")
            print(f"🔍 Fetching images for: {query}")
            item["images"] = fetch_image_links(query)
            time.sleep(1)

    return menu_data

def process_files(input_file: str, output_file: str):
    """Load JSON from input_file, enrich with images, and save to output_file."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {input_file}: {e}")
        return

    updated_menu = enrich_menu_with_images(menu_data)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(updated_menu, f, indent=2)
        print(f"✅ Image-enriched menu saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save {output_file}: {e}")

# Example usage
if __name__ == "__main__":
    process_files("output_menu.json", "output_menu_with_images.json")
