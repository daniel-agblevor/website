/**
 * Slideshow Carousel Module
 * Handles homepage photo slideshow with up to 15 photos, captions, and smooth transitions.
 */
class SlideshowCarousel {
  constructor(containerId, slidesData = []) {
    this.container = document.getElementById(containerId);
    this.slidesData = slidesData;
    this.currentIndex = 0;
    this.autoplayTimer = null;
    this.autoplayInterval = 5000;

    if (this.container && this.slidesData.length > 0) {
      this.init();
    }
  }

  init() {
    this.render();
    this.bindEvents();
    this.startAutoplay();
  }

  render() {
    this.container.innerHTML = `
      <div class="slideshow-wrapper">
        <div class="slideshow-track" id="slideshow-track">
          ${this.slidesData.map((slide) => `
            <div class="slide-item">
              <img src="${slide.image_url}" alt="${slide.caption || 'Event photo'}" loading="lazy">
              ${slide.caption ? `<div class="slide-caption">${slide.caption}</div>` : ''}
            </div>
          `).join('')}
        </div>
        <button class="slideshow-btn prev" id="slide-prev" aria-label="Previous Slide">❮</button>
        <button class="slideshow-btn next" id="slide-next" aria-label="Next Slide">❯</button>
        <div class="slideshow-dots" id="slideshow-dots">
          ${this.slidesData.map((_, i) => `
            <div class="dot ${i === 0 ? 'active' : ''}" data-index="${i}"></div>
          `).join('')}
        </div>
      </div>
    `;
    this.track = this.container.querySelector('#slideshow-track');
    this.dots = this.container.querySelectorAll('.dot');
  }

  bindEvents() {
    const prevBtn = this.container.querySelector('#slide-prev');
    const nextBtn = this.container.querySelector('#slide-next');

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        this.prev();
        this.resetAutoplay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        this.next();
        this.resetAutoplay();
      });
    }

    this.dots.forEach((dot) => {
      dot.addEventListener('click', (e) => {
        const index = parseInt(e.target.getAttribute('data-index'), 10);
        this.goTo(index);
        this.resetAutoplay();
      });
    });
  }

  goTo(index) {
    if (index < 0) index = this.slidesData.length - 1;
    if (index >= this.slidesData.length) index = 0;

    this.currentIndex = index;
    if (this.track) {
      this.track.style.transform = `translateX(-${this.currentIndex * 100}%)`;
    }

    this.dots.forEach((dot, i) => {
      if (i === this.currentIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }

  next() {
    this.goTo(this.currentIndex + 1);
  }

  prev() {
    this.goTo(this.currentIndex - 1);
  }

  startAutoplay() {
    this.autoplayTimer = setInterval(() => this.next(), this.autoplayInterval);
  }

  resetAutoplay() {
    clearInterval(this.autoplayTimer);
    this.startAutoplay();
  }
}
