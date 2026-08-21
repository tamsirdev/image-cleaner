# Image Cleaner for WordPress

A secure web app to clean filenames, resize images, and download them ready for WordPress upload.

**Live App:** https://imageclean.streamlit.app/

## Features

- **Clean filenames** — removes spaces, special characters, converts to lowercase
- **Resize to target** — 1200x630, 1920x1080, 2560x1440, or custom dimensions
- **Scale + pad** — maintains aspect ratio with white padding
- **Format conversion** — keep original, all JPEG, or all PNG
- **Adjustable quality** — JPEG compression slider (1-100)
- **Preview** — see before/after comparison
- **ZIP download** — download all processed images in one click
- **Batch processing** — up to 50 images at once

## Security

- **EXIF metadata stripped** — removes GPS, camera info, hidden data
- **Files re-encoded** — eliminates embedded payloads and steganography
- **Magic bytes verified** — validates actual file content, not just extension
- **No data stored** — all processing happens in-browser, nothing saved server-side
- **File size limits** — max 20MB per file, 50 files per batch

## Quick Start

### Live (Recommended)

Just visit: **https://imageclean.streamlit.app/**

No installation required.

### Local

```bash
git clone https://github.com/tamsirdev/image-cleaner.git
cd image-cleaner
pip install -r requirements.txt
streamlit run image_cleaner_app.py
```

Opens at `http://localhost:8501`

## Usage

1. Open the app in your browser
2. Choose size preset in the sidebar (default: 1200x630)
3. Upload images via drag & drop or file browser
4. Click **Process Images**
5. Preview the before/after results
6. Click **Download as ZIP**
7. Upload cleaned images to WordPress

## Size Presets

| Preset | Dimensions | Best For |
|--------|-----------|----------|
| Featured Image | 1200 x 630 | WordPress posts, social media |
| Full HD | 1920 x 1080 | Banners, hero images |
| 2K | 2560 x 1440 | High-res displays |
| Custom | Your choice | Specific requirements |

## Docker

### Run with Docker

```bash
docker build -t image-cleaner .
docker run -p 8501:8501 image-cleaner
```

### Run with Docker Compose

```bash
docker-compose up
```

### Pull from GitHub Container Registry

```bash
docker pull ghcr.io/tamsirdev/image-cleaner:latest
```

## CI/CD

GitHub Actions workflow runs on every push to `main`:

- **Lint** — flake8 code quality checks
- **Test** — verifies dependencies install correctly
- **Docker** — builds and pushes image to GitHub Container Registry

## Presentations

User guide for DOI staff:

```bash
start presentation/index.html
```

Navigate with arrow keys. Press `F` for fullscreen.

## File Structure

```
image-cleaner/
├── image_cleaner_app.py        # Streamlit web app
├── generate_wxr.py             # WordPress WXR importer
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker build file
├── docker-compose.yml          # Docker Compose config
├── presentation/
│   └── index.html              # User presentation (reveal.js)
├── .github/workflows/ci.yml   # GitHub Actions CI/CD
└── README.md                   # This file
```

## Tech Stack

- **Streamlit** — web framework
- **Pillow** — image processing
- **Docker** — containerization
- **GitHub Actions** — CI/CD
- **reveal.js** — presentation slides

## Author

**Tamsir Njie** — ICT Officer, Department of Information

- GitHub: [tamsirdev](https://github.com/tamsirdev)
- Portfolio: [tamsirdev.github.io](https://tamsirdev.github.io/Personal-Portfolio)

## License

MIT
