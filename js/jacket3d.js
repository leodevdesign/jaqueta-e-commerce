/**
 * Luxury 3D Jacket Engine (Three.js)
 * Clean interactive mouse parallax, dynamic specular lighting & organic float
 * Initial scale 0.84 (Hero) scaling smoothly up to 1.20 (Section 2: Details Matter)
 */

class LuxuryJacket3D {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.jacketGroup = null;
    this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    this.clock = new THREE.Clock();

    this.scrollProgress = 0.0;
    this.targetScrollProgress = 0.0;

    this.section5Progress = 0.0;
    this.targetSection5Progress = 0.0;

    this.init();
  }

  init() {
    this.createScene();
    this.createStudioLighting();
    this.load3DJacketModel();
    this.setupEventListeners();
    this.animate();
  }

  createScene() {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 100);
    this.camera.position.set(0, 0, 4.8);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.28;

    this.container.appendChild(this.renderer.domElement);
  }

  createStudioLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.90);
    this.scene.add(ambientLight);

    // Key Studio Light
    this.keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
    this.keyLight.position.set(2.5, 4.0, 3.5);
    this.scene.add(this.keyLight);

    // Left Subtle Accent Light
    this.leftRim = new THREE.DirectionalLight(0x38bdf8, 2.2);
    this.leftRim.position.set(-4.5, 1.5, 2.0);
    this.scene.add(this.leftRim);

    // Right Subtle Violet Accent Light
    this.rightRim = new THREE.DirectionalLight(0xa855f7, 1.8);
    this.rightRim.position.set(4.5, 1.0, 1.8);
    this.scene.add(this.rightRim);

    // Interactive Specular Mouse Follower Light
    this.specularLight = new THREE.PointLight(0xffffff, 2.0, 6.0);
    this.specularLight.position.set(0, 0, 2.5);
    this.scene.add(this.specularLight);
  }

  load3DJacketModel() {
    this.jacketGroup = new THREE.Group();
    const textureLoader = new THREE.TextureLoader();

    const colorTexture = textureLoader.load('assets/images/jacket-cutout.png', (tex) => {
      tex.minFilter = THREE.LinearMipMapLinearFilter;
      tex.magFilter = THREE.LinearFilter;
      tex.generateMipmaps = true;
    });

    const depthTexture = textureLoader.load('assets/images/jacket-depth.png');
    const normalTexture = textureLoader.load('assets/images/jacket-normal.png');

    // Front Volumetric Displaced Mesh
    const frontGeo = new THREE.PlaneGeometry(3.6, 3.6, 256, 256);
    const frontMat = new THREE.MeshPhysicalMaterial({
      map: colorTexture,
      displacementMap: depthTexture,
      displacementScale: 0.42,
      displacementBias: -0.06,
      normalMap: normalTexture,
      normalScale: new THREE.Vector2(1.2, 1.2),
      roughness: 0.18,
      metalness: 0.85,
      clearcoat: 1.0,
      clearcoatRoughness: 0.08,
      transparent: true,
      alphaTest: 0.03,
      side: THREE.FrontSide
    });

    const frontMesh = new THREE.Mesh(frontGeo, frontMat);
    frontMesh.position.z = 0.02;
    this.jacketGroup.add(frontMesh);

    // Back Depth Mesh
    const backGeo = new THREE.PlaneGeometry(3.6, 3.6, 128, 128);
    const backMat = new THREE.MeshPhysicalMaterial({
      map: colorTexture,
      displacementMap: depthTexture,
      displacementScale: -0.32,
      displacementBias: 0.04,
      normalMap: normalTexture,
      normalScale: new THREE.Vector2(-1.0, -1.0),
      roughness: 0.22,
      metalness: 0.80,
      clearcoat: 0.9,
      clearcoatRoughness: 0.10,
      transparent: true,
      alphaTest: 0.03,
      side: THREE.BackSide
    });

    const backMesh = new THREE.Mesh(backGeo, backMat);
    backMesh.position.z = -0.02;
    backMesh.rotation.y = Math.PI;
    this.jacketGroup.add(backMesh);

    // Subtle floating shadow disc
    const shadowGeo = new THREE.PlaneGeometry(3.2, 1.3);
    const shadowCanvas = document.createElement('canvas');
    shadowCanvas.width = 256;
    shadowCanvas.height = 128;
    const sCtx = shadowCanvas.getContext('2d');
    const sGrad = sCtx.createRadialGradient(128, 64, 5, 128, 64, 110);
    sGrad.addColorStop(0, 'rgba(0, 0, 0, 0.65)');
    sGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    sCtx.fillStyle = sGrad;
    sCtx.fillRect(0, 0, 256, 128);

    const shadowTex = new THREE.CanvasTexture(shadowCanvas);
    const shadowMat = new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, opacity: 0.5 });
    const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
    shadowMesh.position.set(0, -1.85, 0);
    shadowMesh.rotation.x = -Math.PI / 2;
    this.jacketGroup.add(shadowMesh);

    // Initial scale on Section 1: 0.74 (calibrated luxury breathing room)
    this.jacketGroup.scale.set(0.74, 0.74, 0.74);
    this.jacketGroup.position.set(0, 0.02, 0);
    this.scene.add(this.jacketGroup);
  }

  setupEventListeners() {
    window.addEventListener('resize', () => {
      const width = this.container.clientWidth || window.innerWidth;
      const height = this.container.clientHeight || window.innerHeight;

      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    });

    window.addEventListener('mousemove', (e) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;

      this.mouse.targetX = x * 0.32;
      this.mouse.targetY = y * 0.18;

      if (this.specularLight) {
        this.specularLight.position.x = x * 2.8;
        this.specularLight.position.y = y * 2.2;
      }
    });
  }

  setScrollProgress(progress) {
    this.targetScrollProgress = Math.max(0, Math.min(1, progress));
  }

  setSection5Progress(progress) {
    this.targetSection5Progress = Math.max(0, Math.min(1, progress));
  }

  setSection5Anchor(rect, progress) {
    this.targetSection5Progress = Math.max(0, Math.min(1, progress));
    if (rect && this.camera) {
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const vFov = (this.camera.fov * Math.PI) / 180;
      const visibleHeight = 2 * Math.tan(vFov / 2) * this.camera.position.z;
      const visibleWidth = visibleHeight * this.camera.aspect;

      this.sec5TargetX = ((centerX / window.innerWidth) - 0.5) * visibleWidth;
      this.sec5TargetY = -((centerY / window.innerHeight) - 0.5) * visibleHeight - 0.02;
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const elapsedTime = this.clock.getElapsedTime();

    // Smooth lerp scroll progress
    this.scrollProgress += (this.targetScrollProgress - this.scrollProgress) * 0.08;
    this.section5Progress += (this.targetSection5Progress - this.section5Progress) * 0.08;

    if (this.jacketGroup) {
      // Base values for Hero / Section 2
      const sec12Scale = 0.74 + this.scrollProgress * 0.42;
      const sec12PosY = 0.02 - this.scrollProgress * 0.04;
      const sec12PosX = 0.0;
      const sec12PosZ = 0.0 + this.scrollProgress * 0.12;
      const sec12RotY = -this.scrollProgress * 0.04;

      // Section 5 Target values (Dynamically anchored directly inside the stage moldura)
      const isDesktop = window.innerWidth >= 768;
      const sec5PosX = (this.sec5TargetX !== undefined) ? this.sec5TargetX : (isDesktop ? -1.18 : 0.0);
      const sec5PosY = (this.sec5TargetY !== undefined) ? this.sec5TargetY : (isDesktop ? -0.56 : -0.15);
      const sec5PosZ = 0.04;
      const sec5Scale = isDesktop ? 0.52 : 0.45; // Perfectly proportioned inside the 440px moldura box
      const sec5RotY = 0.10;

      // Blended values according to section5Progress (0: Center/Hero, 1: Anchored in Section 5 Moldura)
      const p5 = this.section5Progress;
      const finalPosX = THREE.MathUtils.lerp(sec12PosX, sec5PosX, p5);
      const finalPosY = THREE.MathUtils.lerp(sec12PosY, sec5PosY, p5);
      const finalPosZ = THREE.MathUtils.lerp(sec12PosZ, sec5PosZ, p5);
      const finalScale = THREE.MathUtils.lerp(sec12Scale, sec5Scale, p5);
      const baseRotY = THREE.MathUtils.lerp(sec12RotY, sec5RotY, p5);

      const floatAmp = 0.018 * (1.0 - p5 * 0.4);
      const floatOffset = Math.sin(elapsedTime * 1.4) * floatAmp;

      this.jacketGroup.position.set(finalPosX, finalPosY + floatOffset, finalPosZ);
      this.jacketGroup.scale.set(finalScale, finalScale, finalScale);

      // Mouse inertia tracking
      this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
      this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

      const idleTurn = Math.sin(elapsedTime * 0.35) * 0.07 * (1.0 - this.scrollProgress * 0.2);
      this.jacketGroup.rotation.y = baseRotY + idleTurn + this.mouse.x * 0.40;
      this.jacketGroup.rotation.x = -this.mouse.y * 0.20;
      this.jacketGroup.rotation.z = -this.mouse.x * 0.06;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.LuxuryJacket3D = LuxuryJacket3D;
