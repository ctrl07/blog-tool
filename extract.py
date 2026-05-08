#!/usr/bin/env python3
"""
Blog Extractor - reads URLs from urls.txt and outputs CSV + optional XML

Usage:
    python extract.py                          # CSV + HTML files (default)
    python extract.py --xml                    # also export WordPress XML
    python extract.py --images-zip             # also download images as ZIP
    python extract.py --cdp-url http://host:9222

Chrome must be running with remote debugging enabled:
    chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/chrome-debug
"""
import re
import csv
import sys
import logging
import time
import warnings
import argparse
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

warnings.filterwarnings("ignore", category=ResourceWarning)

from blog_extractor import BlogExtractor, REQUEST_DELAY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def save_to_csv(posts: list, output_dir: str) -> str:
    """Write extracted post data to CSV. Returns output path."""
    path = Path(output_dir) / 'blog_posts.csv'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'url', 'slug', 'title', 'title_tag', 'meta_description',
            'date', 'categories', 'tags', 'images', 'links', 'content',
        ])
        for post in posts:
            if post['status'] != 'success':
                continue
            writer.writerow([
                post.get('url', ''),
                post.get('slug', ''),
                post.get('title', ''),
                post.get('title_tag', ''),
                post.get('meta_description', ''),
                post.get('date', ''),
                ' | '.join(post.get('categories', [])),
                ' | '.join(post.get('tags', [])),
                ' | '.join(img['src'] for img in post.get('images', [])),
                ' | '.join(lnk['url'] for lnk in post.get('links', [])),
                post.get('content', ''),
            ])
    return str(path)


def save_html_files(posts: list, output_dir: str) -> str:
    """Save each post's content as an individual HTML file. Returns directory path."""
    html_dir = Path(output_dir) / 'html'
    html_dir.mkdir(exist_ok=True)

    for post in posts:
        if post['status'] != 'success':
            continue

        slug = post.get('slug') or re.sub(r'[^\w\-]', '_', post.get('title', 'post'))
        title = post.get('title', '')
        content = post.get('content', '')
        date = post.get('date', '')
        url = post.get('url', '')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="description" content="{post.get('meta_description', '')}">
  <title>{title}</title>
</head>
<body>
  <!-- source: {url} | date: {date} -->
  <h1>{title}</h1>
  {content}
</body>
</html>"""

        filename = html_dir / f"{slug}.html"
        # Avoid overwriting if slug collision
        counter = 1
        while filename.exists():
            filename = html_dir / f"{slug}_{counter}.html"
            counter += 1

        filename.write_text(html, encoding='utf-8')

    return str(html_dir)


def download_images_zip(posts: list, output_dir: str) -> str | None:
    """Download all unique image URLs and save as a zip. Returns zip path."""
    seen: set = set()
    entries: list[tuple[str, bytes]] = []

    for post in posts:
        if post['status'] != 'success':
            continue
        for img in post.get('images', []):
            src = img.get('src', '').split('?')[0]
            if not src or src in seen:
                continue
            seen.add(src)
            try:
                resp = requests.get(img['src'], timeout=15, stream=True)
                resp.raise_for_status()
                filename = Path(urlparse(src).path).name or 'image'
                base, ext = (filename.rsplit('.', 1) + [''])[:2]
                safe_name = re.sub(r'[^\w.\-]', '_', filename)
                count = sum(1 for n, _ in entries if n.startswith(base))
                if count:
                    safe_name = f"{base}_{count}.{ext}"
                entries.append((safe_name, resp.content))
                print(f"  Downloaded: {safe_name}")
            except Exception as e:
                print(f"  WARN: Could not download {img['src']}: {e}")

    if not entries:
        return None

    zip_path = Path(output_dir) / 'images.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries:
            zf.writestr(name, data)

    return str(zip_path)


def main():
    parser = argparse.ArgumentParser(description='Extract blog posts to CSV + HTML')
    parser.add_argument('--cdp-url', default='http://localhost:9222',
                        help='Chrome CDP endpoint (default: http://localhost:9222)')
    parser.add_argument('--xml', action='store_true',
                        help='Also export WordPress XML to output/blog_posts.xml')
    parser.add_argument('--images-zip', action='store_true',
                        help='Download all images and save to output/images.zip')
    args = parser.parse_args()

    extractor = BlogExtractor(cdp_url=args.cdp_url)
    urls = extractor.load_urls()

    if not urls:
        print("No URLs found in urls.txt")
        return 1

    print(f"Processing {len(urls)} URLs via Chrome at {args.cdp_url}...")
    success_count = 0
    duplicate_count = 0

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        data = extractor.extract_blog_data(url)

        if data['status'] == 'success':
            print(f"  OK: {data['title']} ({data['content_length']} chars)")
            success_count += 1
        elif data['status'] == 'duplicate':
            print(f"  SKIP: duplicate")
            duplicate_count += 1
        else:
            print(f"  FAIL: {data.get('error', 'unknown error')}")

        if i < len(urls):
            time.sleep(REQUEST_DELAY)

    if extractor.extracted_data:
        csv_path = save_to_csv(extractor.extracted_data, extractor.output_dir)
        print(f"\nCSV:    {csv_path}")

        html_dir = save_html_files(extractor.extracted_data, extractor.output_dir)
        print(f"HTML:   {html_dir}/")

        if args.xml:
            extractor.save_to_xml("blog_posts.xml")
            print(f"XML:    output/blog_posts.xml")

        if args.images_zip:
            print("\nDownloading images...")
            zip_path = download_images_zip(extractor.extracted_data, extractor.output_dir)
            if zip_path:
                print(f"ZIP:    {zip_path}")
            else:
                print("No images to download.")

    extractor.close()

    failed = len(urls) - success_count - duplicate_count
    print(f"\nDone: {success_count} extracted, {duplicate_count} duplicates, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
