# Blog Post Extractor

Extract blog posts from any website and convert them to WordPress-compatible XML format.

**Supports:** WordPress, DealerOn, DealerInspire, Wix, Webflow, Blogger, Squarespace, and more!

---

## Quick Start

### Windows

1. **Double-click `start.bat`**
2. Edit `urls.txt` and add your blog URLs (one per line)
3. Wait for extraction to complete
4. Find `output/blog_posts.xml` and import to WordPress

That's it!

---

## Installation

**What you need:**
- Windows 10+
- Google Chrome (must be installed)
- Python 3.13+ (auto-detected)

**What `start.bat` does:**
1. Auto-installs `uv` package manager (if missing)
2. Installs Python dependencies from `pyproject.toml`
3. Downloads Playwright browser components
4. Launches Chrome with remote debugging
5. Runs the extraction tool

Just double-click `start.bat` and wait 2-5 minutes for the first run.

---

## How to Use

### Step 1: Add URLs

Create or edit `urls.txt` with your blog post URLs (one per line):

```
https://example.com/blog/post-1
https://example.com/blog/post-2
https://example.com/blog/post-3
```

### Step 2: Run Extraction

**Option A: Auto (Recommended)**
```bash
Double-click start.bat
```

**Option B: Manual**
```bash
uv run python extract.py
```

### Step 3: Get Output Files

Files are saved to the `output/` folder:

- **`blog_posts.xml`** — WordPress import file ✅
- **`blog_posts.csv`** — (optional) Post metadata as CSV
- **`images.zip`** — (optional) All blog images

---

## CLI Options

```bash
# Extract XML only
uv run python extract.py

# Export post metadata to CSV
uv run python extract.py --csv

# Download all images as ZIP
uv run python extract.py --images-zip

# Both CSV and images
uv run python extract.py --csv --images-zip

# Custom Chrome endpoint
uv run python extract.py --cdp-url http://localhost:9223
```

---

## CSV Export (`--csv`)

One CSV file with post metadata:

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
| links | Hyperlinks in post (pipe-separated) |

---

## Image Download (`--images-zip`)

Downloads all unique images from extracted posts:

- Deduplicates filenames
- Saves to `output/images.zip`
- Useful for archiving or bulk processing

---

## Importing to WordPress

Once extraction completes:

1. Log into WordPress admin panel
2. Go to **Tools → Import**
3. Click **WordPress** (install plugin if prompted)
4. Click **Choose File** and select `output/blog_posts.xml`
5. Click **Upload file and import**
6. Assign authors (or create new ones)
7. Check **"Download and import file attachments"** to import images
8. Click **Submit**
9. Done! Your posts are now in WordPress

---

## What Gets Extracted

✅ Blog post titles & HTML `<title>` tag
✅ Full content (text, images, formatting preserved)
✅ Meta descriptions (SEO)
✅ Author names
✅ Publication dates
✅ Categories and tags
✅ All hyperlinks (internal and external)
✅ All images (WordPress downloads them on import)

---

## Troubleshooting

### Chrome not found
**Error:** `[ERROR] Chrome not found. Install Google Chrome and re-run.`

**Fix:** Install Google Chrome from [google.com/chrome](https://google.com/chrome)

### Dependencies installation fails
**Error:** `[ERROR] Dependency install failed.`

**Fix:** 
- Check your internet connection
- Run `start.bat` again
- If still failing, run: `uv sync --upgrade`

### Extraction is slow
- Default: 2-5 seconds per URL (with scroll and DOM wait)
- This is normal for live browser extraction
- Bulk jobs with 100+ URLs may take 5-15 minutes

### Images not appearing in WordPress
- Make sure you checked **"Download and import file attachments"** during import
- Images may take a few minutes to download after import
- Use `--images-zip` flag to verify images were extracted

### Website blocks extraction
- Some sites detect and block automated scraping
- Try again later (rate limiting)
- Contact the website owner for API access if permanent

---

## Output Files Reference

| File | Purpose | Use Case |
|---|---|---|
| `blog_posts.xml` | WordPress import format | Import to WordPress |
| `blog_posts.csv` | Post metadata spreadsheet | `--csv` flag |
| `images.zip` | Downloaded images archive | `--images-zip` flag |

---

## Requirements

- **Windows 10+** (Windows only)
- **Google Chrome** (v120+)
- **Python 3.13+** (auto-detected)
- **Internet connection** (for dependencies)

---

## How It Works

The tool uses **Chrome's remote debugging protocol** to extract posts:

1. Launches your Chrome browser with debugging enabled
2. Navigates to each URL
3. Emulates screen CSS (not print styles)
4. Scrolls page to trigger lazy-loaded images
5. Captures fully-rendered HTML
6. Parses content using BeautifulSoup
7. Converts to WordPress XML format
8. Deduplicates posts by content hash
9. Generates CSV/ZIP if requested

This approach ensures **all dynamic content and images load** before extraction, unlike simple HTTP scraping.

---

## Advanced

### Run Chrome on a Different Port

If port 9222 is already in use:

```bash
# Edit start.bat line 50:
start "" !CHROME! --remote-debugging-port=9999 --user-data-dir=C:\chrome-debug

# Then run with matching port:
uv run python extract.py --cdp-url http://localhost:9999
```

### Re-run Without Re-installing

After first run, you don't need to re-run `start.bat`. Just:

```bash
# 1. Add URLs to urls.txt
# 2. Launch Chrome manually:
chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug

# 3. Run extraction:
uv run python extract.py --csv --images-zip
```

---

## Version

**1.0.0** - Initial release

- ✅ CDP-based extraction (live browser)
- ✅ WordPress XML export
- ✅ CSV metadata export
- ✅ Image ZIP download
- ✅ Multi-platform blog support

---

## License

MIT License - Free to use, modify, and distribute.

See [LICENSE](LICENSE) file for details.

---

## Need Help?

**Q: Can I extract from password-protected blogs?**
A: No, blog posts must be publicly accessible.

**Q: Can I move this folder?**
A: Yes, move the entire folder anywhere. Everything is self-contained.

**Q: How do I extract 1000+ posts?**
A: Add all URLs to `urls.txt` and run extraction. It will process them sequentially (one at a time).

**Q: What's the difference between XML and CSV output?**
A: XML is for WordPress import. CSV is for spreadsheets/analysis with metadata (title, date, description, links, etc.).

**Q: Do I need Chrome running already?**
A: No! `start.bat` launches Chrome automatically.

---

## Quick Reference

```
FIRST RUN:
  Double-click start.bat (installs everything)

NEXT RUNS:
  1. Edit urls.txt
  2. Double-click start.bat
  
OR (manual):
  uv run python extract.py

WITH OPTIONS:
  uv run python extract.py --csv --images-zip

OUTPUT:
  Check output/ folder for results

IMPORT:
  WordPress → Tools → Import → blog_posts.xml
```
