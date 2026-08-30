# Zainab Altaweel — Art Portfolio

A standalone gallery site for paintings, sketches, and embroidery — separate from
the academic site. Plain HTML/CSS/JS, deployed to GitHub Pages via GitHub Actions.

Repo: https://github.com/ZainabAltaweel/art-gallary
Live at: `https://zainabaltaweel.github.io/art-gallary/` (once GitHub Pages is enabled — see below)

## Structure

```
site/                     ← everything that gets deployed
  index.html              ← homepage (hero + album grid)
  albums/<slug>/index.html← one masonry-grid gallery page per album
  assets/
    css/style.css
    js/lightbox.js        ← click-to-open lightbox w/ prev-next, captions
    images/<slug>/        ← optimized images (numbered + cover.jpg)
    data/
      gallery.json         ← generated: albums, images, dimensions
      captions.json         ← hand-edit this to add captions (see below)

scripts/                  ← one-time / re-run build tooling (not deployed)
  build_images.py         ← resizes + optimizes raw photos into site/assets/images
  generate_site.py        ← builds the homepage grid + each album page from gallery.json

.github/workflows/deploy.yml  ← publishes site/ to GitHub Pages on every push to main
```

## Adding or editing captions

Open `site/assets/data/captions.json`. It's keyed by album slug, then by image
filename:

```json
{
  "faces": {
    "01.jpg": "A short caption, or a line of poetry."
  }
}
```

- Leave an image out entirely if it has no caption yet — nothing shows in the
  lightbox for it (no empty box).
- Arabic text is detected automatically and rendered right-to-left in the
  Amiri typeface. English stays left-to-right. You can mix languages across
  different images freely.
- No code changes needed — just edit this JSON file, commit, and push. The
  GitHub Action redeploys the whole site automatically.

## Replacing the placeholder hero

The homepage hero (`site/index.html`) is currently a plain dark placeholder
with your name and tagline — no image yet, as requested. To add a full-bleed
photo later:

1. Add the image to `site/assets/images/hero.jpg`.
2. In `site/assets/css/style.css`, find the `.hero` rule and add
   `background-image: url('../images/hero.jpg'); background-size: cover; background-position: center;`
   (keep the existing gradient as a fallback/overlay if you'd like the text
   to stay readable over a busy photo).

## Adding a new album later

1. Put the raw photos in `raw-albums/<new-slug>/<Some Folder Name>/`, numbered
   `1.jpg`, `2.jpg`, … plus one `cover.jpg` (same convention as the existing
   albums — the numbered files become the masonry grid, `cover.jpg` becomes
   the homepage thumbnail).
2. Add an entry to the `ALBUMS` list at the top of `scripts/build_images.py`.
3. Run:
   ```
   python3 scripts/build_images.py
   python3 scripts/generate_site.py
   ```
4. Commit and push `site/` (the raw-albums folder itself doesn't need to be
   committed — keep your originals wherever you already store them).

## Local preview

Because captions load via `fetch()`, opening `index.html` directly by
double-clicking it will work for the homepage and grids, but captions won't
load from `file://`. To preview with captions locally:

```
cd site
python3 -m http.server 8000
```

Then open `http://localhost:8000`. Pushing to GitHub always works correctly
since Pages serves over `https://`.

## Design notes

- Palette: cream `#F5F1E8`, near-black `#141414`, white — no accent color.
- Type: Cormorant Garamond (headlines), Jost (UI/body), Amiri (Arabic captions).
- Album masonry uses CSS multi-column layout (no JS library) so it degrades
  gracefully; column count steps down from 4 → 3 → 2 → 1 as the viewport narrows.
