from typing import Dict, Any
from utils.imagesearch import fetch_image_links

def enrich_menu_item(parsed_menu: Dict[str, Any], slug: str, images_per_item: int = 1) -> Dict[str, Any]:
    for category in parsed_menu.get("menu", []):
        for item in category.get("items", []):
            if item.get("slug", "").strip().lower() == slug.strip().lower():
                query = f"{item['name']} - {item.get('description', '')} - {parsed_menu.get('restaurant_name', '')}"
                print(f"🔍 Fetching images for slug '{slug}' with query: {query}")
                item["images"] = fetch_image_links(query, num_images=images_per_item)
                return parsed_menu

    return {"error": f"❌ Dish with slug '{slug}' not found in menu."}
