# Blog Post Extractor

Extract blog posts from any website and export to CSV, HTML, and WordPress-compatible XML.

**Supports:** WordPress, DealerOn, DealerInspire, Wix, Webflow, Blogger, Squarespace, and more!

---

## Quick Start

### Windows

1. **Double-click `start.bat`**
2. Edit `urls.txt` and add your blog post URLs (one per line)
3. Wait for extraction to complete
4. Find your output in the `output/` folder

That's it!

---

## Installation

**What you need:**
- Windows 10+
- Google Chrome (must be installed)
- Python 3.13+ (auto-detected via `uv`)

**What `start.bat` does:**
1. Auto-installs `uv` package manager
2. Installs Python 3.13 (if missing)
3. Installs Python dependencies from `pyproject.toml`
4. Launches Chrome with remote debugging on port 9222
5. Runs the extraction tool

Just double-click `start.bat` and wait for the first run to complete.

---

## How to Use

### Step 1: Add URLs

Create or edit `urls.txt` with your blog post URLs (one per line):

```
https://example.com/blog/post-1
https://example.com/blog/post-2
https://example.com/blog/post-3
```

Lines starting with `#` are treated as comments and skipped.

### Step 2: Run Extraction

**Option A: Auto (Recommended)**
```
Double-click start.bat
```

**Option B: Manual**
```bash
uv run extract.py
```

### Step 3: Get Output Files

Files are saved to the `output/` folder:

| File | Always? | Description |
|---|---|---|
| `blog_posts.csv` | Yes | Post metadata + content as spreadsheet |
| `html/<slug>.html` | Yes | One HTML file per post (editable) |
| `blog_posts.xml` | `--xml` flag | WordPress import file |
| `images.zip` | `--images-zip` flag | All post images as a ZIP |

---

## CLI Options

```bash
# Default: CSV + HTML files
uv run extract.py

# Also export WordPress XML
uv run extract.py --xml

# Also download all images as ZIP
uv run extract.py --images-zip

# Both XML and images
uv run extract.py --xml --images-zip

# Custom Chrome endpoint
uv run extract.py --cdp-url http://localhost:9223
```

---

## CSV Output (always generated)

`output/blog_posts.csv` — one row per post:

| Column | Description |
|---|---|
| url | Original blog post URL |
| slug | URL path slug (last segment) |
| title | Post title (H1 heading) |
| title_tag | HTML `<title>` tag (includes site name) |
| meta_description | SEO meta description |
| date | Publication date |
| categories | Post categories (pipe-separated) |
| tags | Post tags (pipe-separated) |
| images | Image URLs (pipe-separated) |
| links | Hyperlinks in post body (pipe-separated) |
| content | Full post content (HTML) |

---

## HTML Output (always generated)

`output/html/<slug>.html` — one file per post:

- Editable before importing to WordPress
- Includes meta description in `<head>`
- Source URL and date preserved as HTML comment
- Slug collisions handled automatically (appends `_1`, `_2`, etc.)

---

## WordPress XML Export (`--xml`)

`output/blog_posts.xml` — WordPress WXR format:

1. Log into WordPress admin panel
2. Go to **Tools → Import**
3. Click **WordPress** (install plugin if prompted)
4. Click **Choose File** and select `output/blog_posts.xml`
5. Click **Upload file and import**
6. Assign authors (or create new ones)
7. Check **"Download and import file attachments"** to import images
8. Click **Submit**

---

## Image Download (`--images-zip`)

`output/images.zip` — all unique images from extracted posts:

- Deduplicates by URL (query strings stripped for comparison)
- Safe filenames (special characters replaced)
- Handles filename collisions automatically

---

## What Gets Extracted

- Blog post titles & HTML `<title>` tag
- Full post content (HTML, formatting preserved)
- Meta descriptions (SEO)
- Author names
- Publication dates
- Categories and tags
- All hyperlinks from post body
- All images (referenced by URL; WordPress downloads on import)

## Troubleshooting

### Chrome not found
**Error:** `[ERROR] Chrome not found. Install Google Chrome and re-run.`

**Fix:** Install Google Chrome from [google.com/chrome](https://google.com/chrome)

### Dependencies installation fails
**Error:** `[ERROR] Dependency install failed.`

**Fix:**
- Check your internet connection
- Run `start.bat` again
- If still failing: `uv sync --upgrade`

### Extraction is slow
- Default: 2 seconds between URLs, plus scroll time per page
- This is normal for live browser extraction
- Batch jobs with many URLs will take proportionally longer

### Images not appearing in WordPress
- Make sure you checked **"Download and import file attachments"** during import
- Images may take a few minutes to download after import
- Use `--images-zip` to verify images were extracted before importing

### Website blocks extraction
- Some sites detect and block automated scraping
- Try again after a delay
- Contact the website owner for API access if permanent

---

## How It Works

The tool uses **Chrome's remote debugging protocol (CDP)** — it controls your actual Chrome browser, not a headless one:

1. Connects to Chrome via CDP (port 9222)
2. Opens a new tab for each URL
3. Applies screen CSS (not print styles)
4. Scrolls page to trigger lazy-loaded images
5. Captures fully-rendered HTML
6. Parses with BeautifulSoup
7. Extracts title, metadata, content, images, links
8. Deduplicates posts by content hash (blake2s)
9. Saves CSV, HTML, and optionally XML/ZIP

This ensures **all dynamic content and images load** before extraction.

---

## Advanced

### Run Chrome on a Different Port

If port 9222 is already in use, edit `start.bat`:

```bat
start "" !CHROME! --remote-debugging-port=9999 --user-data-dir=C:\chrome-debug
```

Then run with the matching port:

```bash
uv run extract.py --cdp-url http://localhost:9999
```

### Re-run Without Re-installing

After the first run, you can skip `start.bat` and run manually:

```bash
# 1. Launch Chrome with remote debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug

# 2. Edit urls.txt, then run:
uv run extract.py --xml --images-zip
```

---

## Requirements

- **Windows 10+**
- **Google Chrome** (v120+)
- **Internet connection** (first run only, for dependencies)

---

## Files

| File | Purpose |
|---|---|
| `blog_extractor.py` | Core extraction engine |
| `extract.py` | Blog post extractor entry point |
| `start.bat` | One-click setup and run |
| `pyproject.toml` | Python dependencies |
| `urls.txt` | Input URLs (one per line) |

---

## License

MIT License - Free to use, modify, and distribute.

See [LICENSE](LICENSE) file for details.

---

## Quick Reference

```
FIRST RUN:
  Double-click start.bat

NEXT RUNS:
  1. Edit urls.txt
  2. Double-click start.bat

MANUAL:
  uv run extract.py
  uv run extract.py --xml --images-zip

OUTPUT:
  output/blog_posts.csv     — always
  output/html/<slug>.html   — always
  output/blog_posts.xml     — with --xml
  output/images.zip         — with --images-zip

WORDPRESS IMPORT:
  Tools → Import → WordPress → blog_posts.xml
```
