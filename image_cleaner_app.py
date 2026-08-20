import streamlit as st
from PIL import Image, ImageOps
import io
import os
import re
import zipfile
import tempfile

st.set_page_config(page_title="Image Cleaner for WordPress", page_icon="📷", layout="wide")

st.title("Image Cleaner for WordPress")
st.markdown("Upload images → Clean filenames → Resize to 1200x630 → Download as ZIP")

uploaded_files = st.file_uploader(
    "Upload images",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    help="Select all images in your folder"
)

quality = st.slider("JPEG Quality", 1, 100, 85)

TARGET_WIDTH = 1200
TARGET_HEIGHT = 630


def clean_filename(name):
    name = os.path.splitext(name)[0]
    name = name.replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-zA-Z0-9\-]", "", name)
    name = name.lower()
    return name


def get_extension(original_name):
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


if uploaded_files and st.button("Process Images", type="primary"):
    results = []
    progress = st.progress(0)
    status = st.empty()

    for i, uploaded in enumerate(uploaded_files):
        status.text(f"Processing: {uploaded.name}")

        try:
            img = Image.open(uploaded).convert("RGB")
        except Exception:
            st.warning(f"Skipped {uploaded.name} (not a valid image)")
            continue

        original_name = uploaded.name
        cleaned_name = clean_filename(original_name)
        ext = get_extension(original_name)
        final_name = cleaned_name + ext

        processed = resize_with_padding(img, TARGET_WIDTH, TARGET_HEIGHT)

        buf = io.BytesIO()
        if ext == ".jpg":
            processed.save(buf, format="JPEG", quality=quality)
        else:
            processed.save(buf, format="PNG")
        buf.seek(0)

        results.append((final_name, buf, img.size, processed.size))
        progress.progress((i + 1) / len(uploaded_files))

    status.empty()
    progress.empty()

    if results:
        st.success(f"Processed {len(results)} images")

        st.subheader("Preview")
        cols_per_row = 2
        for idx in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row * 2)
            for j in range(cols_per_row):
                if idx + j >= len(results):
                    break
                name, buf, orig_size, new_size = results[idx + j]
                col_before = cols[j * 2]
                col_after = cols[j * 2 + 1]

                buf.seek(0)
                before_img = Image.open(buf)

                col_before.caption(f"Before: {orig_size[0]}x{orig_size[1]}")
                col_before.image(before_img, use_container_width=True)

                col_after.caption(f"After: {new_size[0]}x{new_size[1]} — {name}")
                col_after.image(before_img, use_container_width=True)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, buf, _, _ in results:
                buf.seek(0)
                zf.writestr(name, buf.read())
        zip_buf.seek(0)

        st.download_button(
            label=f"Download All as ZIP ({len(results)} images)",
            data=zip_buf,
            file_name="cleaned_images.zip",
            mime="application/zip",
            type="primary",
        )
