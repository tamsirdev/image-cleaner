import streamlit as st
from PIL import Image
import io
import os
import re
import zipfile

st.set_page_config(page_title="Image Cleaner", page_icon="🧹", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .stat-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .stat-label {
        color: #666;
        font-size: 0.85rem;
    }
    .file-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
    }
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 8px;
        width: 100%;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Image Cleaner</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Clean filenames + resize + download for WordPress</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")

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

    st.markdown("#### Filename Cleaning")
    st.code("Spaces → hyphens\nSpecial chars → removed\nLowercase applied", language=None)


def clean_filename(name):
    name = os.path.splitext(name)[0]
    name = name.replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-zA-Z0-9\-]", "", name)
    name = name.lower()
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


st.divider()

uploaded_files = st.file_uploader(
    "Drop images here or click to browse",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    st.markdown(f"**{len(uploaded_files)}** images ready to process")

if uploaded_files and st.button("Process Images", type="primary", use_container_width=True):
    results = []
    skipped = []

    progress_bar = st.progress(0, text="Starting...")

    for i, uploaded in enumerate(uploaded_files):
        progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processing {i + 1}/{len(uploaded_files)}: {uploaded.name}")

        try:
            img = Image.open(uploaded).convert("RGB")
        except Exception:
            skipped.append(uploaded.name)
            continue

        original_name = uploaded.name
        cleaned_name = clean_filename(original_name)
        ext = get_extension(original_name, format_option)
        final_name = cleaned_name + ext

        processed = resize_with_padding(img, target_w, target_h)

        buf = io.BytesIO()
        if ext == ".jpg":
            processed.save(buf, format="JPEG", quality=quality)
        else:
            processed.save(buf, format="PNG")
        buf.seek(0)

        orig_kb = uploaded.size / 1024
        new_kb = len(buf.getvalue()) / 1024

        results.append((final_name, buf, img.size, processed.size, orig_kb, new_kb))

    progress_bar.empty()

    if skipped:
        st.warning(f"Skipped {len(skipped)} invalid files: {', '.join(skipped)}")

    if results:
        st.divider()

        total_orig_kb = sum(r[4] for r in results)
        total_new_kb = sum(r[5] for r in results)
        saved = total_orig_kb - total_new_kb

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="stat-box"><div class="stat-number">{len(results)}</div><div class="stat-label">Images Processed</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-box"><div class="stat-number">{target_w}x{target_h}</div><div class="stat-label">Output Size</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-box"><div class="stat-number">{total_new_kb:.0f} KB</div><div class="stat-label">Total Size</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="stat-box"><div class="stat-number">{saved:+.0f} KB</div><div class="stat-label">Size Change</div></div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### Preview")

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
