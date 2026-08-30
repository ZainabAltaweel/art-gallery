/* Lightbox + masonry click handling for album pages.
   Expects a global `ALBUM` object (embedded per-page) shaped like:
   { slug: "faces", images: [{file, width, height}, ...] }
   Captions are loaded at runtime from /assets/data/captions.json so
   Zainab can add them any time without touching this file. */
(function () {
  var ARABIC_RE = /[؀-ۿݐ-ݿ]/;

  function isArabic(text) {
    return ARABIC_RE.test(text);
  }

  function imgSrc(slug, file) {
    return '../../assets/images/' + slug + '/' + file;
  }

  function buildLightbox() {
    var root = document.createElement('div');
    root.className = 'lightbox';
    root.innerHTML =
      '<button class="lightbox__close" aria-label="Close">&times;</button>' +
      '<button class="lightbox__nav lightbox__nav--prev" aria-label="Previous">&#8249;</button>' +
      '<button class="lightbox__nav lightbox__nav--next" aria-label="Next">&#8250;</button>' +
      '<div class="lightbox__figure">' +
        '<img class="lightbox__img" alt="">' +
        '<p class="lightbox__caption" hidden></p>' +
      '</div>' +
      '<div class="lightbox__counter"></div>';
    document.body.appendChild(root);
    return root;
  }

  function init(album) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.masonry__item'));
    if (!items.length) return;

    var lightbox = buildLightbox();
    var imgEl = lightbox.querySelector('.lightbox__img');
    var capEl = lightbox.querySelector('.lightbox__caption');
    var counterEl = lightbox.querySelector('.lightbox__counter');
    var closeBtn = lightbox.querySelector('.lightbox__close');
    var prevBtn = lightbox.querySelector('.lightbox__nav--prev');
    var nextBtn = lightbox.querySelector('.lightbox__nav--next');

    var captions = {};
    fetch('../../assets/data/captions.json')
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (data) { captions = (data && data[album.slug]) || {}; })
      .catch(function () { captions = {}; });

    var current = 0;

    function render() {
      var meta = album.images[current];
      imgEl.src = imgSrc(album.slug, meta.file);
      imgEl.alt = album.title || album.slug;

      var caption = captions[meta.file];
      if (caption && String(caption).trim()) {
        capEl.hidden = false;
        capEl.textContent = caption;
        if (isArabic(caption)) {
          capEl.classList.add('rtl-text');
          capEl.setAttribute('dir', 'rtl');
        } else {
          capEl.classList.remove('rtl-text');
          capEl.setAttribute('dir', 'ltr');
        }
      } else {
        capEl.hidden = true;
        capEl.textContent = '';
      }

      counterEl.textContent = (current + 1) + ' / ' + album.images.length;
    }

    function open(index) {
      current = index;
      render();
      lightbox.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }

    function close() {
      lightbox.classList.remove('is-open');
      document.body.style.overflow = '';
    }

    function step(delta) {
      current = (current + delta + album.images.length) % album.images.length;
      render();
    }

    items.forEach(function (el, i) {
      el.addEventListener('click', function () { open(i); });
    });

    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', function (e) { e.stopPropagation(); step(-1); });
    nextBtn.addEventListener('click', function (e) { e.stopPropagation(); step(1); });

    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) close();
    });

    document.addEventListener('keydown', function (e) {
      if (!lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
  }

  window.PortfolioLightbox = { init: init };
})();
