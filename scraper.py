import re
from urllib.parse import urlparse, urljoin, urlsplit
from bs4 import BeautifulSoup

ALLOWED_DOMAINS = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"}
ALLOWED_PATHS = ["/", "/faculty", "/students", "/research", "/about"]

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """
    Extracts hyperlinks from the response content.
    Converts relative URLs to absolute, removes fragments, and handles errors.
    """
    if resp.status != 200 or resp.raw_response is None:
        return []

    try:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        links = set()

        for link in soup.find_all("a", href=True):
            # Convert relative URLs to absolutesc
            absolute_url = urljoin(url, link["href"])

            # Remove fragment (after #) from the URL
            absolute_url = urlsplit(absolute_url)._replace(fragment='').geturl()

            links.add(absolute_url)

        return list(links)

    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # Ensure the URL uses HTTP or HTTPS
        if parsed.scheme not in {"http", "https"}:
            return False

        # Ensure the URL belongs to allowed domains
        if not any(domain in parsed.netloc for domain in ALLOWED_DOMAINS):
            return False

        # Ensure the URL path is allowed
        if not any(parsed.path.startswith(path) for path in ALLOWED_PATHS):
            return False

        # Avoid URLs with file extensions that are non-webpage (e.g., PDF, images)
        if re.match(r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mp3|mp4|pdf|doc|docx|xls|xlsx|ppt|pptx|exe|zip|rar)$",
                    parsed.path.lower()):
            return False

        # Avoid fragment URLs (i.e., those with #)
        if parsed.fragment:
            return False

        return True

    except Exception as e:
        print(f"Error in is_valid for {url}: {e}")
        return False
