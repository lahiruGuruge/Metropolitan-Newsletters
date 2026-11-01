# Metropolitan News Archive

A searchable Metropolitan Technologies newsletter archive. The private archive contains 34 supplied issues across 2023–2025, comprising 341 newsletter pages. For 2025, June and December have not been supplied.

Features: keyword/phrase search, all/any matching, year/month/category/brand filters, source page reader, full newsletter PDFs, local bookmarks and notes, CSV result exports, grid/list views, shareable search URLs, topic overview, related pages and responsive layouts.

Each result represents a newsletter **page**, sometimes containing multiple stories. Categories are automatically suggested and can overlap. Publication dates follow source filenames because printed headers sometimes conflict. Scanned pages use OCR; important facts should be checked against the page image. Bookmarks and notes are stored only in the visitor's browser.

## Content and access

The hosted archive is owner-private. This public repository contains application code and ingestion tools only. Newsletter PDFs, extracted content and page images are deliberately excluded. The application needs a generated `dist/data.json` and corresponding assets before it can run.

## Add newsletters

Install Python packages from `requirements.txt` and the system tools `tesseract-ocr` and `ghostscript`. Put authorised source PDFs in a local folder using names such as `01. Newsletter January 2025.pdf`.

```sh
python ingest.py /absolute/path/to/newsletters
python prepare_pdfs.py /absolute/path/to/newsletters
```

Imports merge by issue ID with the existing archive, preserving other years. Re-importing an issue replaces that issue only. `ingest.py` extracts text, recognises scanned pages, generates page images and thumbnails, applies suggested categories and reviewed titles, and writes `dist/data.json`. `prepare_pdfs.py` generates web-optimised PDF copies. Review new OCR content and titles against source pages before deploying. Reviewed title corrections live in `title-overrides.json` ; apply curated title corrections through the ingestion workflow.

For a local preview, serve `dist` with any static HTTP server. Deploy that folder using your chosen private hosting workflow. Do not publish internal newsletter content to a public audience without organisational approval.

No backend, remote analytics or third-party runtime dependencies are used. Hosting/access configuration is managed separately from this public source repository.
