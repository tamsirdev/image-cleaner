import streamlit as st
from PIL import Image
import io
import os
import re
import zipfile

APP_VERSION = "1.0.0"
APP_UPDATED = "August 2026"

st.set_page_config(page_title="TamsirDev Image Cleaner", page_icon="🧹", layout="wide")

MAX_FILE_SIZE_MB = 20
MAX_FILE_COUNT = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp",
    b"BM": "image/bmp",
    b"II\x2a\x00": "image/tiff",
    b"MM\x00\x2a": "image/tiff",
}

ALLOWED_MAGIC = set(MAGIC_BYTES.values())

st.markdown("""
<style>
    #MainMenu, footer, header[data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding-top: 0 !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    # Deploy button
    div[data-testid="stDeployButton"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e9ecef;
    }
    .header-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #1a1a2e;
        padding: 1rem 2rem;
        margin: 0 -1rem 1.5rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .header-brand {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header-brand span {
        color: #667eea;
    }
    .header-tagline {
        color: #8892b0;
        font-size: 0.85rem;
        margin: 0;
    }
    .header-badge {
        background: #1e3a5f;
        color: #64ffda;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-family: monospace;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
    }
    .stat-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .stat-label {
        color: #666;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .security-badge {
        background: #d4edda;
        color: #155724;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-size: 0.75rem;
        display: inline-block;
        margin-bottom: 1rem;
        font-family: monospace;
    }
    .footer {
        position: sticky;
        bottom: 0;
        z-index: 999;
        background: #1a1a2e;
        color: #8892b0;
        padding: 1.5rem 2rem;
        margin: 2rem -1rem 0 -1rem;
        font-size: 0.8rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
    }
    .footer a {
        color: #667eea;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    .footer-section {
        margin-bottom: 0.8rem;
    }
    .footer-title {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .footer-divider {
        border-top: 1px solid #2d2d44;
        margin: 0.8rem 0;
    }
    div[data-testid="stDownloadButton"] > button {
        background: #1a1a2e;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        border-radius: 6px;
        width: 100%;
        font-weight: 600;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: #2d2d44;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-bar">
    <div>
        <p class="header-brand">Tamsir<span>Dev</span></p>
        <p class="header-tagline">Secure Image Processing Tool</p>
    </div>
    <div class="header-badge">v{APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Image Cleaner")
st.markdown("Clean filenames, resize to target dimensions, and download images ready for WordPress upload.")
st.markdown('<span class="security-badge">EXIF Stripped | Files Re-encoded | Magic Bytes Verified | No Data Stored</span>', unsafe_allow_html=True)


def detect_image_type(file_bytes):
    for magic, mime in MAGIC_BYTES.items():
        if file_bytes[:len(magic)] == magic:
            return mime
    return None


def sanitize_filename(name):
    name = os.path.splitext(name)[0]
    name = name.replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-zA-Z0-9\-]", "", name)
    name = name.lower()
    if not name:
        name = "unnamed"
    name = name[:100]
    return name


def get_extension(original_name, format_option):
    if format_option == "All JPEG":
        return ".jpg"
    if format_option == "All PNG":
        return ".png"
    ext = os.path.splitext(original_name)[1].lower()
    if ext in (".jpg", ".jpeg", ".bmp", ".tiff", ".webp"):
        return ".jpg"
    return ".png"


def validate_and_load_image(uploaded):
    file_bytes = uploaded.read()
    uploaded.seek(0)

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return None, f"File too large ({len(file_bytes) / 1024 / 1024:.1f}MB > {MAX_FILE_SIZE_MB}MB)"

    if len(file_bytes) < 8:
        return None, "File too small to be a valid image"

    mime = detect_image_type(file_bytes)
    if mime not in ALLOWED_MAGIC:
        return None, f"Not a valid image (detected: {mime or 'unknown'})"

    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.load()
    except Exception:
        return None, "Corrupt or unreadable image file"

    img = img.convert("RGB")

    clean = Image.new(img.mode, img.size)
    clean.paste(img)
    img = clean

    return img, None


def resize_with_padding(img, target_w, target_h):
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h

    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)

    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    background = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
    background.paste(img_resized, offset)
    return background


with st.sidebar:
    st.markdown("### Configuration")

    st.markdown("#### Target Size")
    size_option = st.selectbox(
        "Choose size preset",
        ["1200 x 630 (Featured)", "1920 x 1080 (Full HD)", "2560 x 1440 (2K)", "Custom"],
        label_visibility="collapsed",
    )

    if size_option == "1200 x 630 (Featured)":
        target_w, target_h = 1200, 630
    elif size_option == "1920 x 1080 (Full HD)":
        target_w, target_h = 1920, 1080
    elif size_option == "2560 x 1440 (2K)":
        target_w, target_h = 2560, 1440
    else:
        col1, col2 = st.columns(2)
        target_w = col1.number_input("Width", value=1200, min_value=100, max_value=5000, step=10)
        target_h = col2.number_input("Height", value=630, min_value=100, max_value=5000, step=10)

    st.markdown(f"**Selected:** `{target_w} x {target_h}`")

    st.divider()

    st.markdown("#### Output Format")
    format_option = st.radio("Format", ["Keep original", "All JPEG", "All PNG"], label_visibility="collapsed")

    st.divider()

    st.markdown("#### JPEG Quality")
    quality = st.slider("Quality", 1, 100, 85, label_visibility="collapsed")

    st.divider()

    st.markdown("#### Security Limits")
    st.caption(f"Max file size: {MAX_FILE_SIZE_MB}MB")
    st.caption(f"Max files per batch: {MAX_FILE_COUNT}")
    st.caption("EXIF metadata: stripped")
    st.caption("Image re-encoding: enabled")
    st.caption("Magic bytes: verified")

    st.divider()

    st.markdown("#### Filename Rules")
    st.caption("Spaces replaced with hyphens")
    st.caption("Special characters removed")
    st.caption("Lowercase applied")
    st.caption("Max 100 characters")


st.divider()

st.markdown('<p class="section-title">Upload Images</p>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drop images here or click to browse",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    if len(uploaded_files) > MAX_FILE_COUNT:
        st.error(f"Too many files ({len(uploaded_files)} > {MAX_FILE_COUNT}). Maximum allowed is {MAX_FILE_COUNT} files per batch.")
        uploaded_files = None
    else:
        st.markdown(f"**{len(uploaded_files)}** images loaded and ready for processing")

if uploaded_files and st.button("Process Images", type="primary", use_container_width=True):
    results = []
    skipped = []

    progress_bar = st.progress(0, text="Initializing...")

    for i, uploaded in enumerate(uploaded_files):
        progress_bar.progress(
            (i + 1) / len(uploaded_files),
            text=f"Processing {i + 1}/{len(uploaded_files)}: {uploaded.name}",
        )

        img, error = validate_and_load_image(uploaded)
        if error:
            skipped.append((uploaded.name, error))
            continue

        original_name = uploaded.name
        cleaned_name = sanitize_filename(original_name)
        ext = get_extension(original_name, format_option)
        final_name = cleaned_name + ext

        processed = resize_with_padding(img, target_w, target_h)

        buf = io.BytesIO()
        if ext == ".jpg":
            processed.save(buf, format="JPEG", quality=quality, exif=b"")
        else:
            processed.save(buf, format="PNG", exif=b"")
        buf.seek(0)

        orig_kb = uploaded.size / 1024
        new_kb = len(buf.getvalue()) / 1024

        results.append((final_name, buf, img.size, processed.size, orig_kb, new_kb))

    progress_bar.empty()

    if skipped:
        st.warning(f"Skipped {len(skipped)} file(s):")
        for name, reason in skipped:
            st.caption(f"  - **{name}**: {reason}")

    if results:
        st.divider()

        st.markdown('<p class="section-title">Results</p>', unsafe_allow_html=True)

        total_orig_kb = sum(r[4] for r in results)
        total_new_kb = sum(r[5] for r in results)
        saved = total_orig_kb - total_new_kb

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="stat-box"><div class="stat-number">{len(results)}</div><div class="stat-label">Processed</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-box"><div class="stat-number">{target_w}x{target_h}</div><div class="stat-label">Output Size</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-box"><div class="stat-number">{total_new_kb:.0f} KB</div><div class="stat-label">Total Size</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="stat-box"><div class="stat-number">{saved:+.0f} KB</div><div class="stat-label">Size Change</div></div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<p class="section-title">Preview</p>', unsafe_allow_html=True)

        for idx in range(0, len(results), 2):
            cols = st.columns(4)
            for j in range(2):
                if idx + j >= len(results):
                    break
                name, buf, orig_size, new_size, orig_kb, new_kb = results[idx + j]

                with cols[j * 2]:
                    buf.seek(0)
                    before_img = Image.open(buf)
                    st.image(before_img, caption=f"Before: {orig_size[0]}x{orig_size[1]} ({orig_kb:.0f} KB)", use_container_width=True)

                with cols[j * 2 + 1]:
                    st.image(before_img, caption=f"After: {name} ({new_kb:.0f} KB)", use_container_width=True)

        st.divider()

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, buf, _, _, _, _ in results:
                buf.seek(0)
                zf.writestr(name, buf.read())
        zip_buf.seek(0)

        st.download_button(
            label=f"Download {len(results)} images as ZIP",
            data=zip_buf,
            file_name="cleaned_images.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

st.markdown(f"""
<div class="footer">
    <div class="footer-section">
        <div class="footer-title">Security Policy</div>
        All uploaded images are processed in memory and never stored on the server. Files are re-encoded to strip embedded payloads. EXIF metadata (GPS, camera info, hidden data) is removed. Magic bytes are verified to confirm file type.
    </div>
    <div class="footer-divider"></div>
    <div class="footer-section">
        <div class="footer-title">File Limits</div>
        Maximum {MAX_FILE_SIZE_MB}MB per file | Maximum {MAX_FILE_COUNT} files per batch | Supported: JPEG, PNG, WebP, BMP, TIFF
    </div>
    <div class="footer-divider"></div>
    <div class="footer-section">
        Version {APP_VERSION} | Last updated {APP_UPDATED} | <a href="https://github.com/tamsirdev/image-cleaner" target="_blank">GitHub</a> | &copy; 2026 Tamsir Njie. All rights reserved.
    </div>
</div>
""", unsafe_allow_html=True)
