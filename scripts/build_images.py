#!/usr/bin/env python3
"""
Processes raw album folders into optimized web images + gallery.json
for the Zainab Altaweel art portfolio site.
"""
import json
import os
import re
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()

RAW_DIR = Path("/home/claude/portfolio-site/raw-albums")
OUT_IMG_DIR = Path("/home/claude/portfolio-site/site/assets/images")
DATA_DIR = Path("/home/claude/portfolio-site/site/assets/data")

# slug -> (source subfolder name, display title)
ALBUMS = [
    ("alnahrain-university", "alnahrain-university", "Alnahrain University"),
    ("ballerina", "ballerina", "Ballerina"),
    ("colorful", "Watercolors", "Colorful"),
    ("embroidery", "Embroidery", "Embroidery"),
    ("faces", "Faces", "Faces"),
    ("in-memory-of-my-mother", "In Memory of My Mother", "In Memory of My Mother"),
    ("mediterranean-still-life", "Mediterranean Still Life", "Mediterranean Still Life"),
    ("pencil-ink-sketches", "Pencile Ink Sketches", "Pencil & Ink Sketches"),
]

GALLERY_MAX_EDGE = 2000
COVER_MAX_EDGE = 1600
JPEG_QUALITY = 84

NUMERIC_RE = re.compile(r"^(\d+)\.")


def load_image(path: Path) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # normalize rotation
    return im


def has_real_alpha(im: Image.Image) -> bool:
    if im.mode not in ("RGBA", "LA", "P"):
        return False
    im2 = im.convert("RGBA")
    alpha = im2.getchannel("A")
    return alpha.getextrema()[0] < 255


def save_optimized(im: Image.Image, dest: Path, max_edge: int):
    w, h = im.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)

    dest.parent.mkdir(parents=True, exist_ok=True)

    if has_real_alpha(im):
        im = im.convert("RGBA")
        out_path = dest.with_suffix(".png")
        im.save(out_path, "PNG", optimize=True)
    else:
        im = im.convert("RGB")
        out_path = dest.with_suffix(".jpg")
        im.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    return out_path, im.size


def main():
    OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    gallery = []

    for slug, src_subfolder, title in ALBUMS:
        src_dir = RAW_DIR / slug / src_subfolder
        if not src_dir.is_dir():
            raise SystemExit(f"Missing source dir: {src_dir}")

        files = sorted(os.listdir(src_dir))

        # cover
        cover_file = next((f for f in files if f.lower().startswith("cover.")), None)
        if not cover_file:
            raise SystemExit(f"No cover image found for album {slug}")
        cover_im = load_image(src_dir / cover_file)
        cover_out, cover_size = save_optimized(cover_im, OUT_IMG_DIR / slug / "cover", COVER_MAX_EDGE)

        # numbered gallery images, in numeric order
        numbered = []
        for f in files:
            m = NUMERIC_RE.match(f)
            if m:
                numbered.append((int(m.group(1)), f))
        numbered.sort(key=lambda t: t[0])

        images = []
        for num, fname in numbered:
            im = load_image(src_dir / fname)
            out_path, size = save_optimized(im, OUT_IMG_DIR / slug / f"{num:02d}", GALLERY_MAX_EDGE)
            images.append({
                "file": out_path.name,
                "width": size[0],
                "height": size[1],
            })

        gallery.append({
            "slug": slug,
            "title": title,
            "cover": cover_out.name,
            "count": len(images),
            "images": images,
        })

        print(f"{slug}: cover={cover_out.name} {cover_size}, {len(images)} images")

    gallery.sort(key=lambda a: a["title"])

    with open(DATA_DIR / "gallery.json", "w", encoding="utf-8") as f:
        json.dump(gallery, f, indent=2, ensure_ascii=False)

    captions_path = DATA_DIR / "captions.json"
    if not captions_path.exists():
        skeleton = {a["slug"]: {} for a in gallery}
        with open(captions_path, "w", encoding="utf-8") as f:
            json.dump(skeleton, f, indent=2, ensure_ascii=False)

    print("\nDone. Albums:", len(gallery))
    print("Total images:", sum(a["count"] for a in gallery))


if __name__ == "__main__":
    main()
