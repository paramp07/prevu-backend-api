import os
import json
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from dotenv import load_dotenv

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Param\Documents\Credentials\my-vertexai-project-464302-302be09a449a.json"


# --- Set environment variables BEFORE importing vertexai ---
load_dotenv()  # Loads from .env by default

# Now access them like this:
GOOGLE_VERTEX_LOCATION = os.environ["GOOGLE_VERTEX_LOCATION"]
GOOGLE_VERTEX_PROJECT = os.environ["GOOGLE_VERTEX_PROJECT"]

# --- Config ---
PROJECT_ID = GOOGLE_VERTEX_PROJECT
LOCATION = GOOGLE_VERTEX_LOCATION
OUTPUT_FILE = "output_menu.json"

# --- Menu Parser Function ---
def extract_menu_data(raw_text: str) -> dict:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    system_prompt = """
        You are an AI that parses OCR-scanned restaurant menus into clean, structured JSON for use in apps, image generation systems, and databases.

        Your responsibilities:

        1. Clean up and correct spelling or grammar issues in the text.
        2. Extract the restaurant name and location, if found.
        3. Generate a brief 1–2 sentence description of the restaurant’s style or cuisine.
        4. Organize the dishes into standardized food categories (see list below).
        5. Output each category with a personalized description that includes the restaurant name (if found).
        6. For each dish, return detailed fields including name, description, price, tags, a unique slug and ID, an image prompt, and an empty list in the `images` field.
        7. Follow the rules below exactly to ensure reliable, valid JSON output.

        ---

        ### Output JSON Format

        ```json
        {
          "restaurant_name": "string (if found)",
          "location": "string (if found)",
          "description": "Brief description of the restaurant or menu style",
          "currency": "USD",
          "last_updated": "2025-07-02T00:00:00Z",
          "restaurant_image": "", 
          "menu": [
            {
              "category": "Appetizers",
              "description": "At [RESTAURANT_NAME], small dishes served at the beginning of a meal to stimulate the appetite.",
              "priority": 2,
              "items": [
                {
                  "id": "appetizers_bruschetta",
                  "name": "Bruschetta",
                  "slug": "bruschetta",
                  "description": "Grilled bread topped with tomatoes, garlic, basil, and olive oil.",
                  "price": "6.95",
                  "tags": ["vegetarian", "italian", "starter"],
                  "image_prompt": "An elegant photo of bruschetta on grilled bread, with tomatoes and basil, served at [RESTAURANT_NAME]",
                  "images": []
                }
              ]
            }
          ]
        }
        rules:
        - Please format all names (restaurant name, category names, and dish names) in proper title case (e.g., "Italian Restaurant", "Main Courses / Entrees", "Lasagna") instead of all uppercase.
        - Keep descriptions and other text natural and properly capitalized.
        - restaurant_name and location: Extract if available; return null if missing.
        - description: One to two sentences summarizing the restaurant.
        - currency: Always return "USD".
        - last_updated: Use the current date in ISO 8601 format.
        - Add an empty restaurant_image field at the top level of the output JSON for future use.

        - Category:
          - Use the most fitting category from the list below.
          - If restaurant_name is found, begin the description with: “At [RESTAURANT_NAME], …”.
          - Assign a priority (1–5) based on importance (e.g., Main Courses = 1, Beverages = 5).

        - Item Fields:
          - id: Combine lowercase category and item name with underscores (e.g., main_courses_steak_frites).
          - slug: Hyphenated, lowercase item name (e.g., steak-frites).
          - description: Use null if not found.
          - price: DONT include a dollar sign, only return integar or null if missing.
          - tags: Include relevant keywords (e.g., "vegan", "thai", "dessert").
          - image_prompt: Short, vivid sentence combining the item, its appearance, and the restaurant name if found.
          - images: Always include an empty list (e.g., "images": []) to store image URLs or references in the future.

        - Do not hallucinate missing fields. If any data is missing in the source text, return null or omit the key.

        - Standard Categories (use closest match):
          - Appetizers / Starters
          - Main Courses / Entrees
          - Sides / Accompaniments
          - Desserts
          - Beverages
          - Salads
          - Soups
          - Sandwiches / Wraps
          - Specials / Chef’s Picks
          - Kids' Menu
          - Breakfast / Brunch / Lunch / Dinner

        - If no section headers are found, infer the category from context.

        - Format all output as valid, clean JSON suitable for use in production systems.
    """

    model = GenerativeModel("gemini-2.0-flash-lite")

    response = model.generate_content([
        system_prompt.strip(),
        f"Here is the raw OCR text from a restaurant menu:\n\n{raw_text.strip()}"
    ])

    content = response.text.strip()

    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_text = content[json_start:json_end]
        parsed_data = json.loads(json_text)

        # ✅ Ensure 'images' and 'id' are present
        for idx, item in enumerate(parsed_data.get("menu_items", []), start=1):
            item["images"] = item.get("images", [])
            item["id"] = str(idx)

        # 💾 Save to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2)
        print(f"✅ Output saved to: {OUTPUT_FILE}")

        return parsed_data

    except Exception as e:
        print("⚠️ JSON parsing failed:", e)
        print("Raw response:", content)
        return {}

# --- Example usage ---
if __name__ == "__main__":
    sample_text = """
    AVOCADO TOAST 400-500 Cal
    Gourmet Bagel, everything seasoning, salt & pepper

    Chorizo Sunrise 800 Cal
    Eggs, Chorizo, Cheese, Avocado, Jalapeno Salsa Shmear on Green Chile Bagel

    All-Nighter $7.95
    Eggs, Bacon, American Cheese, Jalapeno Aioli on a Cheesy Hash Brown

    The Daily Bagel Co - Austin, TX
    """

    result = extract_menu_data(sample_text)
    print(json.dumps(result, indent=2))
