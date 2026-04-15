# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Project Overview

A blog post extraction tool that reads URLs from `urls.txt`, scrapes each post via a live Chrome browser, and outputs a WordPress-compatible XML file (`output/blog_posts.xml`).

**Platform:** Windows only  
**Browser:** Google Chrome via CDP (no headless)  
**Entry point:** `python extract.py`

---

## Architecture

Two files:

- **`blog_extractor.py`** — `BlogExtractor` class. All scraping, parsing, and export logic.
- **`extract.py`** — Thin runner. Reads `urls.txt`, calls the extractor, saves XML.

---

## How It Runs

Chrome must be running with remote debugging enabled before `extract.py` is called. `test.bat` handles this automatically.

```
urls.txt
  → load_urls()
  → [for each URL] extract_blog_data()
      → fetch_content()          # CDP: bring_to_front → goto → emulate_media → JS scroll → settle
      → detect_platform()        # from parsed HTML
      → extract_title/author/date/categories/tags()
      → extract_content()        # platform-specific selectors → clean_html → html_to_gutenberg
      → duplicate hash check
  → save_to_xml()  →  output/blog_posts.xml
```

---

## Critical Constraints — DO NOT CHANGE

### 1. BeautifulSoup `formatter="minimal"`

**Location:** `_convert_relative_urls_to_absolute()`

```python
soup.decode(formatter="minimal")  # MUST stay "minimal"
```

Without this, BeautifulSoup inserts line breaks inside long `href` attributes. WordPress truncates URLs split across lines during XML import, breaking all links.  
Never use `formatter="html"` or `formatter="html5"`.

### 2. HTTPS URLs in WordPress XML

**Location:** `_write_xml_post()`, `_write_xml_attachment()`

Always write resolved HTTPS URLs into the XML — never `file://` paths. WordPress fetches images from the URL in `<wp:attachment_url>` during import. A local path is invisible to the server.

### 3. blake2s Content Hashing for Deduplication

**Location:** `get_content_hash()`, `extract_blog_data()`

```python
hashlib.blake2s(content.encode('utf-8')).hexdigest()
```

Hashes post body content (not title) to skip duplicate posts across different URLs. Do not switch to MD5 (not FIPS-compliant) or hash the URL (same content at different URLs would not be deduplicated).

### 4. BS4 Multi-Valued `rel` Attribute

**Location:** `extract_categories()`, `extract_tags()`

BeautifulSoup stores `rel="category tag"` as a Python list `['category', 'tag']`. Searching with `rel='category tag'` (string) silently matches nothing.

```python
# CORRECT
soup.find_all('a', rel=lambda r: r and 'category' in r)

# BROKEN — string never matches a list
soup.find_all('a', rel='category tag')
```

### 5. CDP Page Lifecycle

**Location:** `fetch_content()`

- Connect once per URL with `sync_playwright()` context manager
- Get the existing context: `browser.contexts[0]`
- Always close the **page** in `finally` — never close the browser (it's the user's Chrome)
- `page.bring_to_front()` before `goto` so the tab is visible and rendering correctly

---

## Fetch Behaviour

`fetch_content()` follows the miniwayback pattern:

1. `page.bring_to_front()`
2. `page.goto(url, wait_until="commit", timeout=30000)`
3. `page.emulate_media(media="screen")` — screen CSS, not print
4. JS `setInterval` scroll — scrolls by `window.innerHeight` until bottom, then back to top
5. `page.wait_for_timeout(settle_delay)` — default 5 s after scrolling

---

## Category / Tag Extraction

Extraction order (first match wins for categories):

1. DealerInspire: `div.meta-below-content a[rel~=category]`
2. DealerOn: `div.blog__entry__content__categories a`
3. DealerOn v2: `div.categories a`
4. WordPress `rel="category"` links (lambda match)
5. WordPress CSS: `.cat-links a`, `.entry-categories a`, `.post-categories a`
6. Wix: `ul[aria-label="Post categories"] a`
7. Meta fallback: `meta[name/property="article:section"]`

Tags follow same pattern using `rel="tag"` (lambda) + `.tags-links a`, `.entry-tags a`, `.post-tags a`, and `meta[property="article:tag"]`.

---

## Image Handling

`download_images=False` by default — images are referenced by HTTPS URL in the XML and WordPress downloads them during import.

When `download_images=True`:
- `_resolve_image_url()` follows redirects on WebDAM/dealer.com dynamic endpoints to get permanent S3 URLs (strips signed query params)
- `_download_image()` saves to `output/images/` as a local backup
- XML still uses the HTTPS URL, not the local path

---

## Files

| File | Purpose |
|---|---|
| `blog_extractor.py` | Core engine |
| `extract.py` | Entry point |
| `requirements.txt` | Dependencies |
| `test.bat` | One-click setup (uv + deps + Playwright) and run |
| `LICENSE` | License |

**Setup:**
```
test.bat
```

**Run manually:**
```
python extract.py
python extract.py --cdp-url http://localhost:9222
```

Chrome must be running with:
```
chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug
```
