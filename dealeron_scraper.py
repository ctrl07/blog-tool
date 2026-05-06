#!/usr/bin/env python3
"""
DealerOn Full Site Content Scraper

Reads URLs from urls.txt, scrapes each page via live Chrome CDP session,
and exports full page content to output/dealeron_site.csv.

Usage:
    python dealeron_scraper.py
    python dealeron_scraper.py --cdp-url http://localhost:9222

Chrome must be running with remote debugging enabled:
    chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/chrome-debug
"""

import argparse
import csv
import logging
import sys
import time
import warnings
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from blog_extractor import BlogExtractor, REQUEST_DELAY

warnings.filterwarnings("ignore", category=ResourceWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ── Page type detection ────────────────────────────────────────────────────────

def detect_page_type(url: str) -> str:
    path = urlparse(url).path.lower().rstrip('/')
    if not path or path == '':
        return 'home'
    if '/blog/' in path or path.endswith('/blog'):
        return 'blog_post'
    if '/service' in path:
        return 'service'
    if '/about' in path:
        return 'about'
    if '/specials' in path or '/offers' in path:
        return 'specials'
    if '/inventory' in path:
        return 'inventory'
    if '/contact' in path:
        return 'contact'
    return 'page'


# ── Content extraction ─────────────────────────────────────────────────────────

_CONTENT_SELECTORS = [
    'div.blog__article__content__text',   # DealerOn blog content
    'div.blog__entry__content',           # DealerOn blog fallback
    'div.editor',                         # DealerOn variant
    'div.rich-text-block',                # Webflow
    'main',
    'article',
    '.content',
    'body',                               # last resort
]

_STRIP_TAGS = {'script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside'}


def extract_body_text(soup: BeautifulSoup) -> str:
    """Find main content area and return clean plain text."""
    content_el = None
    for selector in _CONTENT_SELECTORS:
        content_el = soup.select_one(selector)
        if content_el:
            break

    if not content_el:
        return ''

    for tag in content_el.find_all(_STRIP_TAGS):
        tag.decompose()

    text = content_el.get_text(separator=' ', strip=True)
    # Collapse whitespace
    return ' '.join(text.split())


def extract_internal_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Return unique internal links found on the page."""
    domain = urlparse(base_url).netloc
    seen: set = set()
    links: list[str] = []
    for a in soup.find_all('a', href=True):
        href = str(a['href']).strip()
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        if href.startswith('/'):
            href = f"{urlparse(base_url).scheme}://{domain}{href}"
        parsed = urlparse(href)
        if parsed.netloc == domain and href not in seen:
            seen.add(href)
            links.append(href)
    return links


# ── Scraper ───────────────────────────────────────────────────────────────────

def scrape_page(extractor: BlogExtractor, url: str) -> dict:
    """Scrape a single DealerOn page and return extracted data."""
    html = extractor.fetch_content(url)
    if not html:
        return {'status': 'failed', 'url': url, 'error': 'Could not fetch page'}

    soup = BeautifulSoup(html, 'html.parser')
    slug = url.rstrip('/').split('/')[-1] or ''
    title = extractor.extract_title(soup)
    title_tag = extractor.extract_title_tag(soup)
    meta_description = extractor.extract_meta_description(soup)
    body_text = extract_body_text(soup)
    word_count = len(body_text.split()) if body_text else 0
    internal_links = extract_internal_links(soup, url)

    return {
        'status': 'success',
        'url': url,
        'slug': slug,
        'page_type': detect_page_type(url),
        'title': title,
        'title_tag': title_tag,
        'meta_description': meta_description,
        'word_count': word_count,
        'body_text': body_text,
        'internal_links': ' | '.join(internal_links),
    }


def save_to_csv(rows: list[dict], output_dir: str) -> str:
    """Write scraped data to CSV. Returns output path."""
    path = Path(output_dir) / 'dealeron_site.csv'
    columns = [
        'url', 'slug', 'page_type', 'title', 'title_tag',
        'meta_description', 'word_count', 'body_text', 'internal_links',
    ]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            if row['status'] == 'success':
                writer.writerow(row)
    return str(path)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description='Scrape DealerOn site pages to CSV')
    parser.add_argument('--cdp-url', default='http://localhost:9222',
                        help='Chrome CDP endpoint (default: http://localhost:9222)')
    args = parser.parse_args()

    extractor = BlogExtractor(cdp_url=args.cdp_url)
    urls = extractor.load_urls()

    if not urls:
        print("No URLs found in urls.txt")
        return 1

    print(f"Scraping {len(urls)} DealerOn pages via Chrome at {args.cdp_url}...")
    rows: list[dict] = []
    success = failed = 0

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        result = scrape_page(extractor, url)

        if result['status'] == 'success':
            print(f"  OK  [{result['page_type']}] {result['title']} ({result['word_count']} words)")
            rows.append(result)
            success += 1
        else:
            print(f"  FAIL: {result.get('error', 'unknown error')}")
            failed += 1

        if i < len(urls):
            time.sleep(REQUEST_DELAY)

    extractor.close()

    if rows:
        csv_path = save_to_csv(rows, extractor.output_dir)
        print(f"\nCSV:  {csv_path}")

    print(f"Done: {success} scraped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
