import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from rapidfuzz import process, fuzz

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

def scrape_menu_page_html_body_only(restaurant_url, output_filename="menu.html"):
    response = requests.get(restaurant_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch homepage: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    base_domain = urlparse(restaurant_url).netloc
    links = set()
    for a in soup.find_all("a", href=True):
        href = a['href']
        full_url = urljoin(restaurant_url, href)
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)

    link_paths = [urlparse(link).path.lower() for link in links]

    query = "menu"
    matches = process.extract(query, link_paths, scorer=fuzz.ratio, limit=None)

    # Filter matches with score >= 60
    good_matches = [(path, score) for path, score, _ in matches if score >= 60]
    if not good_matches:
        raise Exception("No menu-like page with score >= 60 found")

    # Pick highest scoring link
    best_path, best_score = max(good_matches, key=lambda x: x[1])
    best_menu_url = f"{urlparse(restaurant_url).scheme}://{base_domain}{best_path}"

    menu_response = requests.get(best_menu_url, headers=HEADERS)
    if menu_response.status_code != 200:
        raise Exception(f"Failed to fetch menu page: {menu_response.status_code}")

    menu_soup = BeautifulSoup(menu_response.text, "html.parser")
    body_content = menu_soup.body
    if not body_content:
        raise Exception("No <body> tag found in menu page")

    # Save just the body inner HTML (contents inside <body> tag)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(str(body_content))

    print(f"Menu page body saved to {output_filename}")

if __name__ == "__main__":
    restaurant_homepage = "https://torchystacos.com"  # Replace with your URL
    scrape_menu_page_html_body_only(restaurant_homepage)
