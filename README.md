# Image Cleaner for WordPress

A simple web app to clean filenames, resize images to 1200x630, and download them as a ZIP for WordPress uploads.

## Features

- **Clean filenames** — removes spaces, special characters, converts to lowercase
- **Resize to 1200x630** — standard WordPress featured image size
- **Scale + pad** — maintains aspect ratio with white padding
- **Keep original format** — JPEG stays JPEG, PNG stays PNG
- **Adjustable quality** — JPEG compression slider (1-100)
- **Preview** — see before/after comparison
- **ZIP download** — download all processed images in one click

## Quick Start

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
git clone https://github.com/tamsirdev/image-cleaner.git
cd image-cleaner
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run image_cleaner_app.py
```

The app will open at `http://localhost:8501`

## Usage

1. Open the app in your browser
2. Click **Browse files** and select all images from your folder
3. Adjust the **JPEG Quality** slider if needed (default: 85)
4. Click **Process Images**
5. Preview the before/after results
6. Click **Download All as ZIP**
7. Extract the ZIP and upload to WordPress

## WordPress Import (Bonus)

The `generate_wxr.py` script creates a WordPress WXR import file from a text file of articles:

```bash
python generate_wxr.py
```

Then import `wordpress_import.xml` via **Tools > Import > WordPress** in your admin dashboard.

## File Structure

```
image-cleaner/
├── image_cleaner_app.py   # Streamlit web app
├── generate_wxr.py        # WordPress WXR importer
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Tech Stack

- **Streamlit** — web framework
- **Pillow** — image processing

## License

MIT
