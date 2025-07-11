import os
import json
import vertexai
from vertexai.preview.generative_models import GenerativeModel

from dotenv import load_dotenv

# --- Set environment variables BEFORE importing vertexai ---
load_dotenv()  # Loads from .env by default

# Now access them like this:
GOOGLE_VERTEX_LOCATION = os.environ["GOOGLE_VERTEX_LOCATION"]
GOOGLE_VERTEX_PROJECT = os.environ["GOOGLE_VERTEX_PROJECT"]
GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
# --- Config ---
PROJECT_ID = os.environ["GOOGLE_VERTEX_PROJECT"]
LOCATION = os.environ["GOOGLE_VERTEX_LOCATION"]
OUTPUT_FILE = "output_menu.json"


# --- Menu Parser Function ---
def extract_menu_data(raw_text: str) -> dict:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    system_prompt = """
        You are an AI that parses OCR-scanned restaurant menus into structured JSON.

        Return the output in this format:
        {
          "restaurant_name": "string (if found)",
          "location": "string (if found)",
          "description": "brief description of the restaurant or menu style",
          "menu_items": [
            {
              "id": "string (must be unique for each dish)",
              "title": "Name of the dish",
              "description": "Short description of ingredients or what it is",
              "price": float (only the number, e.g. 8.99),
              "calories": integer (best guess, pick average if range, remove 'cal'),
              "images": []
            }
          ]
        }

        Rules:
        - Only return valid JSON.
        - `id` must be a string and unique per item (e.g. "1", "2", etc.).
        - `price` should not include "$" or text. If not found, set to null.
        - `calories` must be a single integer. If given a range (e.g. 400-600), use the average (e.g. 500). If not found, set to null.
        - `images` must always be present as an empty list.
        - Ignore decorative or irrelevant lines.
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
