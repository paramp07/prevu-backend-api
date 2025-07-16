import os
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

IGNORE_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.mp3', '.mp4', '.avi',
    '.mov', '.wmv', '.flv', '.mkv', '.ico'
)

def get_internal_links(url, base_domain):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if not href or href.startswith('javascript:') or href.startswith('mailto:'):
                continue

            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.netloc != base_domain:
                continue

            if '/wp-content/' in parsed.path or '/wp-admin/' in parsed.path:
                continue

            if parsed.path.lower().endswith(IGNORE_EXTENSIONS):
                continue

            normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
            links.add(normalized_url)

        return list(links)
    except Exception:
        return []

def save_html(url, html, folder="saved_menus"):
    os.makedirs(folder, exist_ok=True)
    parsed = urlparse(url)
    # create a safe filename from path, replacing '/' with '_', or use 'index' for root
    filename = parsed.path.strip("/").replace("/", "_") or "index"
    filename += ".html"
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved {url} as {filepath}")

def crawl_menu_pages(start_url, base_domain, visited=None, max_depth=3, depth=0):
    if visited is None:
        visited = set()

    if depth > max_depth or start_url in visited:
        return

    print(f"Crawling (depth {depth}): {start_url}")
    visited.add(start_url)

    try:
        response = requests.get(start_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            print(f"Failed to fetch {start_url} - status code: {response.status_code}")
            return
        html = response.text
    except Exception as e:
        print(f"Error fetching {start_url}: {e}")
        return

    internal_links = get_internal_links(start_url, base_domain)
    # Remove already visited links
    internal_links = [link for link in internal_links if link not in visited]

    if not internal_links:
        # No more internal links - save this page
        save_html(start_url, html)
    else:
        # Recursively crawl child menu pages
        for link in internal_links:
            crawl_menu_pages(link, base_domain, visited, max_depth, depth + 1)

# Example usage:
if __name__ == "__main__":
    menu_url = "https://tinplatepizza.com/menu"  # Replace with your menu page URL
    base_domain = urlparse(menu_url).netloc
    crawl_menu_pages(menu_url, base_domain, max_depth=2)
