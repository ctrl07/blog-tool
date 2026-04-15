#!/usr/bin/env python3
"""
Blog Extractor - reads URLs from urls.txt and outputs WordPress XML to output/blog_posts.xml

Usage:
    python extract.py                          # default CDP at http://localhost:9222
    python extract.py --cdp-url http://host:9222

Chrome must be running with remote debugging enabled:
    chrome.exe --remote-debugging-port=9222 --user-data-dir=C:/chrome-debug
"""

import sys
import logging
import time
import warnings
import argparse

warnings.filterwarnings("ignore", category=ResourceWarning)

from blog_extractor import BlogExtractor, REQUEST_DELAY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    parser = argparse.ArgumentParser(description='Extract blog posts to WordPress XML')
    parser.add_argument('--cdp-url', default='http://localhost:9222',
                        help='Chrome CDP endpoint (default: http://localhost:9222)')
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
        extractor.save_to_xml("blog_posts.xml")

    failed = len(urls) - success_count - duplicate_count
    print(f"\nDone: {success_count} extracted, {duplicate_count} duplicates, {failed} failed")
    print(f"Output: output/blog_posts.xml")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
