/**
 * Collection Cards 3D Interactive Turntable Viewer (Three.js + GLTFLoader)
 * Renders true 3D .GLB models exported from Blender directly inside the luxury product cards.
 * Features:
 * - 360° Drag & Orbit with smooth damping
 * - Idle auto-spin
 * - Responsive sizing & IntersectionObserver optimization (only renders when in view)
 * - PBR lighting with specular accents
 */

class CollectionCards3D {
  constructor() {
    this.cards = [];
    this.loader = new THREE.GLTFLoader();
    this.isIntersecting = false;
    this.init();
  }

  init() {
    const containers = document.querySelectorAll('.card-3d-container');
    if (!containers.length) return;

    // Observe visibility to conserve GPU/CPU
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.isIntersecting = true;
          this.cards.forEach(card => card.isVisible = true);
        } else {
          this.cards.forEach(card => card.isVisible = false);
        }
      });
    }, { threshold: 0.1 });

    const collectionsSection = document.getElementById('collections');
    if (collectionsSection) {
      observer.observe(collectionsSection);
    }

    containers.forEach((container, index) => {
      const modelPath = container.getAttribute('data-model');
      const lightColor = container.getAttribute('data-light') || '#ffffff';
      if (modelPath) {
        this.setupCard(container, modelPath, lightColor, index);
      }
    });

    this.animate();
  }

  setupCard(container, modelPath, lightColorHex, index) {
    const width = container.clientWidth || 280;
    const height = container.clientHeight || 190;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
    camera.position.set(0, 0, 3.8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    const neutralStudio = container.dataset.studio === 'neutral';
    if (neutralStudio) {
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.toneMappingExposure = 0.55;
    }
    if (container.dataset.studio === 'photographic') {
      // Source photographs already contain lighting; preserve their RGB colors.
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.toneMapping = THREE.NoToneMapping;
      renderer.toneMappingExposure = 1;
    }

    const canvasEl = renderer.domElement;
    canvasEl.className = 'absolute inset-0 w-full h-full z-15 pointer-events-auto opacity-0 transition-opacity duration-700';
    container.appendChild(canvasEl);

    // Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, neutralStudio ? 0.55 : 1.2);
    scene.add(ambientLight);

    const lightColor = new THREE.Color(lightColorHex);

    const keyLight = new THREE.DirectionalLight(0xffffff, neutralStudio ? 1.0 : 2.4);
    keyLight.position.set(2.0, 3.0, 3.5);
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(neutralStudio ? 0xffffff : lightColor, neutralStudio ? 0.7 : 2.5);
    rimLight.position.set(-2.5, 1.5, -2.0);
    scene.add(rimLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, neutralStudio ? 0.35 : 1.1);
    fillLight.position.set(0, -2.0, 2.0);
    scene.add(fillLight);

    const cardState = {
      container,
      renderer,
      scene,
      camera,
      modelGroup: null,
      isDragging: false,
      previousMousePosition: { x: 0, y: 0 },
      rotationVelocity: { x: 0, y: 0 },
      targetRotation: { x: 0, y: 0 },
      idleSpeed: 0.007,
      isVisible: true
    };

    // Load GLB model exported from Blender
    this.loader.load(
      modelPath,
      (gltf) => {
        const model = gltf.scene;

        // Auto-center and fit model perfectly
        const box = new THREE.Box3().setFromObject(model);
        const center = new THREE.Vector3();
        box.getCenter(center);
        const size = new THREE.Vector3();
        box.getSize(size);

        // Center local origin to exact mesh centroid
        model.position.x = -center.x;
        model.position.y = -center.y;
        model.position.z = -center.z;

        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 2.25 / maxDim;

        // Enhance material properties
        model.traverse((child) => {
          if (child.isMesh && child.material && container.dataset.preserveMaterials !== 'true') {
            child.material.roughness = 0.22;
            child.material.metalness = 0.85;
            child.material.needsUpdate = true;
          }
        });

        const pivotGroup = new THREE.Group();
        pivotGroup.add(model);
        pivotGroup.scale.set(scale, scale, scale);
        pivotGroup.position.set(0, 0, 0);

        scene.add(pivotGroup);
        cardState.modelGroup = pivotGroup;

        // Reveal 3D canvas and fade placeholder image smoothly
        setTimeout(() => {
          canvasEl.classList.remove('opacity-0');
          canvasEl.classList.add('opacity-100');
          const placeholderImg = container.querySelector('.card-placeholder-img');
          if (placeholderImg) {
            placeholderImg.classList.add('opacity-0');
          }
        }, 120);
      },
      undefined,
      (err) => {
        console.warn(`Could not load GLB for card ${index} (${modelPath}):`, err);
      }
    );

    // Interactive Drag / Orbit Controls
    const startDrag = (x, y) => {
      cardState.isDragging = true;
      cardState.previousMousePosition = { x, y };
      container.style.cursor = 'grabbing';
    };

    const moveDrag = (x, y) => {
      if (!cardState.isDragging || !cardState.modelGroup) return;
      const deltaX = x - cardState.previousMousePosition.x;
      const deltaY = y - cardState.previousMousePosition.y;

      cardState.targetRotation.y += deltaX * 0.012;
      cardState.targetRotation.x = Math.max(-0.4, Math.min(0.4, cardState.targetRotation.x + deltaY * 0.008));

      cardState.previousMousePosition = { x, y };
    };

    const endDrag = () => {
      cardState.isDragging = false;
      container.style.cursor = 'grab';
    };

    container.addEventListener('mousedown', (e) => startDrag(e.clientX, e.clientY));
    window.addEventListener('mousemove', (e) => moveDrag(e.clientX, e.clientY));
    window.addEventListener('mouseup', endDrag);

    // Touch support for mobile/trackpad
    container.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) startDrag(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1) moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });

    window.addEventListener('touchend', endDrag);

    // Window Resize handling
    window.addEventListener('resize', () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      if (newWidth && newHeight) {
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
      }
    });

    this.cards.push(cardState);
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    this.cards.forEach((card) => {
      if (!card.isVisible || !card.modelGroup) return;

      if (!card.isDragging) {
        // Continuous slow idle spin
        card.targetRotation.y += card.idleSpeed;
      }

      // Smooth damping interpolation
      card.modelGroup.rotation.y += (card.targetRotation.y - card.modelGroup.rotation.y) * 0.08;
      card.modelGroup.rotation.x += (card.targetRotation.x - card.modelGroup.rotation.x) * 0.08;

      card.renderer.render(card.scene, card.camera);
    });
  }
}

window.CollectionCards3D = CollectionCards3D;
