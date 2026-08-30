#!/usr/bin/env python3
"""Generates index.html's album grid and each albums/<slug>/index.html page
from assets/data/gallery.json. Run after build_images.py."""
import json
from pathlib import Path

SITE = Path("/home/claude/portfolio-site/site")
DATA = SITE / "assets" / "data" / "gallery.json"

ALBUM_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Zainab Altaweel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Jost:wght@300;400;500&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>

<header class="topbar topbar--light">
  <a class="brand" href="../../index.html">Zainab Altaweel</a>
  <a class="back-link" href="../../index.html">&larr; All Albums</a>
</header>

<header class="album-header">
  <p class="album-header__count">{count_label}</p>
  <h1 class="album-header__title display">{title}</h1>
</header>

{grid_html}

<script type="application/json" id="album-data">{album_json}</script>
<script src="../../assets/js/lightbox.js"></script>
<script>
  var ALBUM = JSON.parse(document.getElementById('album-data').textContent);
  PortfolioLightbox.init(ALBUM);
</script>
</body>
</html>
"""


def card_html(album):
    return f"""  <a class="album-card" href="albums/{album['slug']}/index.html">
    <div class="album-card__frame">
      <div class="album-card__mat">
        <img src="assets/images/{album['slug']}/{album['cover']}" alt="{album['title']} cover" loading="lazy">
      </div>
    </div>
    <div class="album-card__caption">
      <span class="album-card__title display">{album['title']}</span>
      <span class="album-card__count">{album['count']:02d}</span>
    </div>
  </a>"""


def grid_item_html(slug, image):
    ratio = image["width"] / image["height"] if image["height"] else 1
    return (
        f'  <figure class="masonry__item" style="aspect-ratio:{ratio:.4f}">'
        f'<img src="../../assets/images/{slug}/{image["file"]}" '
        f'width="{image["width"]}" height="{image["height"]}" '
        f'loading="lazy" alt=""></figure>'
    )


def main():
    albums = json.loads(DATA.read_text(encoding="utf-8"))

    # --- index.html album grid ---
    index_path = SITE / "index.html"
    html = index_path.read_text(encoding="utf-8")
    grid_html = "\n".join(card_html(a) for a in albums)
    marker = '<div class="album-grid" id="album-grid"><!-- populated by build script --></div>'
    assert marker in html, "album-grid marker not found in index.html"
    html = html.replace(marker, f'<div class="album-grid" id="album-grid">\n{grid_html}\n  </div>')
    index_path.write_text(html, encoding="utf-8")

    # --- per-album pages ---
    for album in albums:
        slug = album["slug"]
        out_dir = SITE / "albums" / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        if album["images"]:
            grid_html = '<main class="masonry">\n' + "\n".join(
                grid_item_html(slug, img) for img in album["images"]
            ) + "\n</main>"
        else:
            grid_html = '<p class="empty-note">More from this album coming soon.</p>'

        count_label = f"{album['count']:02d} works" if album["count"] != 1 else "01 work"

        page = ALBUM_TEMPLATE.format(
            title=album["title"],
            count_label=count_label,
            grid_html=grid_html,
            album_json=json.dumps(
                {"slug": slug, "title": album["title"], "images": album["images"]},
                ensure_ascii=False,
            ),
        )
        (out_dir / "index.html").write_text(page, encoding="utf-8")

    print(f"Generated homepage grid + {len(albums)} album pages.")


if __name__ == "__main__":
    main()
