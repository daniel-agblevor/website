/**
 * Animations & Smooth Scroll Initializer
 * Uses Lenis for smooth scrolling paired with GSAP ScrollTrigger section reveals.
 */
document.addEventListener('DOMContentLoaded', () => {
  initLenis();
  initGSAPAnimations();
});

function initLenis() {
  if (typeof Lenis === 'undefined') return;

  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    smoothTouch: false
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);

  // Synchronize Lenis with GSAP ScrollTrigger if loaded
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  }
}

function initGSAPAnimations() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  // Hero section entrance animation
  gsap.from('.hero-content > *', {
    y: 40,
    opacity: 0,
    duration: 1,
    stagger: 0.15,
    ease: 'power3.out'
  });

  gsap.from('.hero-visual', {
    scale: 0.95,
    opacity: 0,
    duration: 1.2,
    delay: 0.3,
    ease: 'power3.out'
  });

  // Section reveals
  const sections = document.querySelectorAll('.section');
  sections.forEach((section) => {
    const cards = section.querySelectorAll('.glass-panel');
    if (cards.length > 0) {
      gsap.from(cards, {
        scrollTrigger: {
          trigger: section,
          start: 'top 80%',
          toggleActions: 'play none none none'
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power2.out'
      });
    }
  });
}
