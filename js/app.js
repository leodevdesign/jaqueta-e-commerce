/**
 * Luxury Storefront Controller
 * Section 1 (Hero) & Section 2 (Details Matter) Scroll Orchestration & Cart Management
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize 3D Luxury Jacket Engine (Hero & Section 2)
  let jacketEngine = null;
  try {
    jacketEngine = new LuxuryJacket3D('canvas3d-container');
    window.jacketEngine = jacketEngine;
  } catch (err) {
    console.error('Error initializing 3D Jacket Engine:', err);
  }

  // Initialize Collection Cards 3D Viewports (Section 3 Blender GLB models)
  try {
    if (window.CollectionCards3D) {
      window.collectionCards3D = new CollectionCards3D();
    }
  } catch (err) {
    console.error('Error initializing Collection Cards 3D:', err);
  }

  // Subtle Luxury Audio Feedback
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  function playLuxuryClick(pitch = 1000) {
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
    osc.type = 'sine';
    osc.frequency.setValueAtTime(pitch, now);
    osc.frequency.exponentialRampToValueAtTime(300, now + 0.03);
    gain.gain.setValueAtTime(0.04, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.03);
    osc.start(now);
    osc.stop(now + 0.03);
  }

  // Bind subtle audio on hover
  document.querySelectorAll('button, a, .luxury-detail-card').forEach(el => {
    el.addEventListener('mouseenter', () => playLuxuryClick(1200));
  });

  // Cart Counter Interaction
  let cartCount = 0;
  const cartBtn = document.getElementById('btn-cart');
  const cartCountEl = document.getElementById('cart-count');
  const buyBtns = document.querySelectorAll('.btn-buy-trigger');

  buyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playLuxuryClick(600);
      cartCount++;
      if (cartCountEl) {
        cartCountEl.textContent = cartCount;
        cartBtn.classList.add('scale-105');
        setTimeout(() => {
          cartBtn.classList.remove('scale-105');
        }, 200);
      }
    });
  });

  // Scroll Choreography (Hero -> Details Matter)
  const handleScroll = () => {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    const progress = Math.min(1.0, Math.max(0.0, scrollY / (windowHeight * 0.9)));

    if (jacketEngine) {
      jacketEngine.setScrollProgress(progress);
    }

    const canvasContainer = document.getElementById('canvas3d-container');
    const heroContent = document.getElementById('hero-content');
    const heroFooter = document.getElementById('hero-footer');

    if (heroContent) {
      const heroOpacity = Math.max(0, 1 - progress * 1.5);
      heroContent.style.opacity = heroOpacity;
      heroContent.style.transform = `translateY(${-progress * 40}px)`;
      heroContent.style.pointerEvents = heroOpacity > 0.1 ? 'auto' : 'none';
    }

    if (heroFooter) {
      const footerOpacity = Math.max(0, 1 - progress * 1.8);
      heroFooter.style.opacity = footerOpacity;
      heroFooter.style.pointerEvents = footerOpacity > 0.1 ? 'auto' : 'none';
    }

    // Section 5: Transition and Anchor the 3D Jacket directly inside the stage moldura
    const faqSec = document.getElementById('faq-specs');
    const stageEl = document.getElementById('jacket-sec5-stage');
    let section5Progress = 0;

    if (faqSec && stageEl) {
      const faqRect = faqSec.getBoundingClientRect();
      const stageRect = stageEl.getBoundingClientRect();
      const enterThreshold = windowHeight * 0.95;

      if (faqRect.top < enterThreshold) {
        section5Progress = Math.max(0, Math.min(1, (enterThreshold - faqRect.top) / (windowHeight * 0.65)));
      }

      if (jacketEngine) {
        jacketEngine.setSection5Anchor(stageRect, section5Progress);
      }

      // Keep canvas visible while stage is in view; smoothly fade out when scrolled past stage
      if (canvasContainer) {
        if (section5Progress > 0.01) {
          let opacity = Math.min(1, section5Progress * 1.5);
          if (stageRect.bottom < windowHeight * 0.25) {
            opacity = Math.max(0, stageRect.bottom / (windowHeight * 0.25));
          }
          canvasContainer.style.opacity = opacity;
        } else if (scrollY > windowHeight * 1.2) {
          const fadeOut = Math.max(0, 1 - (scrollY - windowHeight * 1.2) / (windowHeight * 0.4));
          canvasContainer.style.opacity = fadeOut;
        } else {
          canvasContainer.style.opacity = 1;
        }
      }
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // GSAP Initial Entrance Animation
  if (window.gsap) {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.from('#site-header', { y: -40, opacity: 0, duration: 1.1 })
      .from('.hud-left', { x: -50, opacity: 0, duration: 1.0 }, '-=0.7')
      .from('.hud-right', { x: 50, opacity: 0, duration: 1.0 }, '-=0.8')
      .from('#hero-footer', { opacity: 0, duration: 1.0 }, '-=0.7')
      .from('#canvas3d-container', { scale: 0.92, opacity: 0, duration: 1.4 }, '-=1.1');
  }

  // Section 4: Technology Exploded Layer Strata Interactivity
  const layerSelectors = document.querySelectorAll('.tech-layer-selector');
  const hudCards = document.querySelectorAll('.hud-annotation-card');

  function activateLayer(layerId) {
    layerSelectors.forEach(sel => {
      if (sel.getAttribute('data-layer-target') === String(layerId)) {
        sel.classList.add('active');
        const chevron = sel.querySelector('svg, i');
        if (chevron) chevron.style.color = '#38bdf8';
      } else {
        sel.classList.remove('active');
        const chevron = sel.querySelector('svg, i');
        if (chevron) chevron.style.color = '#64748b';
      }
    });

    hudCards.forEach(card => {
      if (card.id === `hud-card-${layerId}`) {
        card.classList.add('revealed');
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  layerSelectors.forEach(sel => {
    const layerId = sel.getAttribute('data-layer-target');
    sel.addEventListener('mouseenter', () => {
      playLuxuryClick(1400);
      activateLayer(layerId);
    });
    sel.addEventListener('click', () => {
      playLuxuryClick(1600);
      activateLayer(layerId);
    });
  });

  hudCards.forEach((card, idx) => {
    const layerId = idx + 1;
    card.addEventListener('mouseenter', () => {
      playLuxuryClick(1200);
      activateLayer(layerId);
    });
  });

  // Section 5: Specifications FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-accordion-item');
  faqItems.forEach(item => {
    const header = item.querySelector('.faq-accordion-header');
    if (header) {
      header.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');
        playLuxuryClick(isOpen ? 1000 : 1350);
        item.classList.toggle('open');
      });
    }
  });

  // Back to Top Button
  const btnBackToTop = document.getElementById('btn-back-to-top');
  if (btnBackToTop) {
    btnBackToTop.addEventListener('click', () => {
      playLuxuryClick(900);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  /* ========================================================
     BRAND PRELOADER CONTROLLER (Stroke -> Left-to-Right Fill)
     ======================================================== */
  const preloader = document.getElementById('site-preloader');
  const wipeRect = document.getElementById('aetherWipeRect');
  const laserLine = document.getElementById('preloader-laser-line');
  const fillBar = document.getElementById('preloader-fill-bar');
  const pctText = document.getElementById('preloader-pct');
  const statusMsg = document.getElementById('preloader-status-msg');

  if (preloader && wipeRect && fillBar && pctText) {
    let progress = 0;
    const duration = 1600; // ms for the left-to-right fill wipe
    const startTime = performance.now() + 500; // start wipe after stroke outline has drawn in

    const statusPhases = [
      { threshold: 0.20, text: 'CALIBRATING TITANIUM MATRIX...' },
      { threshold: 0.45, text: 'INITIALIZING 4-TIER STRATA...' },
      { threshold: 0.70, text: 'SYNTHESIZING AEROGEL CORE...' },
      { threshold: 0.90, text: 'ENGAGING TELEMETRY DOCK...' },
      { threshold: 1.00, text: 'SYSTEM ONLINE // ARCHIVE READY' }
    ];

    function animatePreloader(now) {
      if (now < startTime) {
        requestAnimationFrame(animatePreloader);
        return;
      }

      const elapsed = now - startTime;
      progress = Math.min(elapsed / duration, 1.0);

      // Smooth cubic ease-out
      const eased = 1 - Math.pow(1 - progress, 2.2);
      const pctValue = Math.floor(eased * 100);

      wipeRect.setAttribute('width', `${(eased * 100).toFixed(2)}%`);
      fillBar.style.width = `${(eased * 100).toFixed(2)}%`;
      pctText.textContent = `${pctValue.toString().padStart(2, '0')}%`;

      if (laserLine) {
        laserLine.style.left = `${(eased * 100).toFixed(2)}%`;
        laserLine.style.opacity = progress > 0.02 && progress < 0.98 ? '1' : '0';
      }

      for (const phase of statusPhases) {
        if (progress <= phase.threshold) {
          if (statusMsg) statusMsg.textContent = phase.text;
          break;
        }
      }

      if (progress < 1.0) {
        requestAnimationFrame(animatePreloader);
      } else {
        // 100% Complete
        wipeRect.setAttribute('width', '100%');
        fillBar.style.width = '100%';
        pctText.textContent = '100%';
        if (statusMsg) statusMsg.textContent = 'SYSTEM ONLINE // ARCHIVE READY';
        if (laserLine) laserLine.style.opacity = '0';

        setTimeout(() => {
          preloader.classList.add('loaded');
          playLuxuryClick(1800);
          setTimeout(() => {
            playLuxuryClick(2400);
          }, 120);

          setTimeout(() => {
            preloader.style.display = 'none';
          }, 950);
        }, 350);
      }
    }

    requestAnimationFrame(animatePreloader);
  }

  /* ========================================================
     CUSTOM LUXURY CURSOR & GLOW CONTROLLER
     ======================================================== */
  const cursorDot = document.getElementById('luxury-cursor-dot');
  const cursorRing = document.getElementById('luxury-cursor-ring');
  const cursorGlow = document.getElementById('luxury-cursor-glow');

  if (cursorDot && cursorRing && cursorGlow) {
    let mouseX = -200;
    let mouseY = -200;
    let ringX = -200;
    let ringY = -200;
    let glowX = -200;
    let glowY = -200;
    let isVisible = false;

    // Keep hidden initially
    cursorDot.style.opacity = '0';
    cursorRing.style.opacity = '0';
    cursorGlow.style.opacity = '0';

    window.addEventListener('mousemove', (e) => {
      // Guard: do not show cursor while preloader is active
      const activePreloader = document.getElementById('site-preloader');
      if (activePreloader && !activePreloader.classList.contains('loaded')) {
        return;
      }

      mouseX = e.clientX;
      mouseY = e.clientY;
      if (!isVisible) {
        isVisible = true;
        ringX = mouseX;
        ringY = mouseY;
        glowX = mouseX;
        glowY = mouseY;
        cursorDot.style.opacity = '1';
        cursorRing.style.opacity = '1';
        cursorGlow.style.opacity = '0.85';
      }
      cursorDot.style.left = `${mouseX}px`;
      cursorDot.style.top = `${mouseY}px`;
    });

    document.addEventListener('mouseleave', () => {
      isVisible = false;
      cursorDot.style.opacity = '0';
      cursorRing.style.opacity = '0';
      cursorGlow.style.opacity = '0';
    });

    document.addEventListener('mouseenter', () => {
      const activePreloader = document.getElementById('site-preloader');
      if (activePreloader && !activePreloader.classList.contains('loaded')) {
        return;
      }
      isVisible = true;
      cursorDot.style.opacity = '1';
      cursorRing.style.opacity = '1';
      cursorGlow.style.opacity = '0.85';
    });

    function renderCursor() {
      if (isVisible) {
        ringX += (mouseX - ringX) * 0.22;
        ringY += (mouseY - ringY) * 0.22;
        cursorRing.style.left = `${ringX.toFixed(2)}px`;
        cursorRing.style.top = `${ringY.toFixed(2)}px`;

        glowX += (mouseX - glowX) * 0.08;
        glowY += (mouseY - glowY) * 0.08;
        cursorGlow.style.left = `${glowX.toFixed(2)}px`;
        cursorGlow.style.top = `${glowY.toFixed(2)}px`;
      }
      requestAnimationFrame(renderCursor);
    }
    requestAnimationFrame(renderCursor);

    const interactiveTargets = 'a, button, input, textarea, [role="button"], .color-bullet, .tech-layer-selector, .hud-floating-card, .faq-accordion-header, .luxury-detail-card, .collection-card, .btn-luxury-action';
    
    document.addEventListener('mouseover', (e) => {
      if (e.target.closest(interactiveTargets)) {
        cursorRing.classList.add('hovered');
        cursorGlow.classList.add('hovered');
      }
    });

    document.addEventListener('mouseout', (e) => {
      if (e.target.closest(interactiveTargets)) {
        cursorRing.classList.remove('hovered');
        cursorGlow.classList.remove('hovered');
      }
    });

    window.addEventListener('mousedown', () => {
      cursorRing.classList.add('clicking');
    });
    window.addEventListener('mouseup', () => {
      cursorRing.classList.remove('clicking');
    });
  }
});


