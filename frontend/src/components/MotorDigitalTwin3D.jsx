import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

export function MotorDigitalTwin3D({ telemetry, healthData }) {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const shaftRef = useRef(null);
  const fanRef = useRef(null);
  const statorMeshRef = useRef(null);
  const motorGroupRef = useRef(null);

  // Store live physics telemetry values in ref for animation frame loop
  const telemetryRef = useRef({
    rpm: 0,
    temp: 45,
    vib: 1.2,
    state: 'NORMAL'
  });

  useEffect(() => {
    if (telemetry) {
      telemetryRef.current = {
        rpm: telemetry.rpm || 0,
        temp: telemetry.temperature || 45,
        vib: telemetry.vibration_rms || 1.2,
        state: telemetry.operating_state || 'NORMAL'
      };
    }
  }, [telemetry]);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    const width = currentMount.clientWidth;
    const height = currentMount.clientHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color('#0d1322');

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(4, 3, 5);
    camera.lookAt(0, 0, 0);

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      currentMount.appendChild(renderer.domElement);
    } catch (e) {
      console.warn('[MotorDigitalTwin3D] WebGL not supported in current environment:', e);
      return;
    }

    // 2. Lighting Setup (Industrial Studio)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight1.position.set(5, 8, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xf59e0b, 0.4);
    dirLight2.position.set(-5, -2, -5);
    scene.add(dirLight2);

    // 3. Construct Industrial Motor 3D Model
    const motorGroup = new THREE.Group();
    motorGroupRef.current = motorGroup;
    scene.add(motorGroup);

    // Base Mounting Feet
    const feetGeo = new THREE.BoxGeometry(2.4, 0.15, 1.6);
    const feetMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const feetMesh = new THREE.Mesh(feetGeo, feetMat);
    feetMesh.position.y = -0.75;
    motorGroup.add(feetMesh);

    // Main Stator Cylinder Body
    const statorGeo = new THREE.CylinderGeometry(0.85, 0.85, 1.8, 32);
    const statorMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      metalness: 0.6,
      roughness: 0.3
    });
    const statorMesh = new THREE.Mesh(statorGeo, statorMat);
    statorMesh.rotation.z = Math.PI / 2;
    statorMeshRef.current = statorMesh;
    motorGroup.add(statorMesh);

    // Stator Cooling Fins
    const finCount = 12;
    for (let i = 0; i < finCount; i++) {
      const angle = (i / finCount) * Math.PI * 2;
      const finGeo = new THREE.BoxGeometry(1.6, 0.08, 0.12);
      const finMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 });
      const finMesh = new THREE.Mesh(finGeo, finMat);
      finMesh.position.set(0, Math.sin(angle) * 0.88, Math.cos(angle) * 0.88);
      finMesh.rotation.x = angle;
      motorGroup.add(finMesh);
    }

    // Terminal Box (Top Junction Box)
    const boxGeo = new THREE.BoxGeometry(0.5, 0.35, 0.5);
    const boxMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 });
    const boxMesh = new THREE.Mesh(boxGeo, boxMat);
    boxMesh.position.set(0, 1.05, 0);
    motorGroup.add(boxMesh);

    // Rotating Shaft (Output Axle)
    const shaftGeo = new THREE.CylinderGeometry(0.18, 0.18, 2.8, 24);
    const shaftMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.9, roughness: 0.1 });
    const shaftMesh = new THREE.Mesh(shaftGeo, shaftMat);
    shaftMesh.rotation.z = Math.PI / 2;
    shaftMesh.position.x = 0.4;
    shaftRef.current = shaftMesh;
    motorGroup.add(shaftMesh);

    // Shaft Keyway Indicator Notch
    const notchGeo = new THREE.BoxGeometry(0.5, 0.05, 0.05);
    const notchMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
    const notchMesh = new THREE.Mesh(notchGeo, notchMat);
    notchMesh.position.set(1.1, 0.16, 0);
    shaftMesh.add(notchMesh);

    // Rear Cooling Fan Guard
    const fanGeo = new THREE.CylinderGeometry(0.75, 0.75, 0.3, 16);
    const fanMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, wireframe: true });
    const fanMesh = new THREE.Mesh(fanGeo, fanMat);
    fanMesh.rotation.z = Math.PI / 2;
    fanMesh.position.x = -1.0;
    fanRef.current = fanMesh;
    motorGroup.add(fanMesh);

    // 4. Add Sensor Markers Around Motor
    const createSensorMarker = (x, y, z, labelColor) => {
      const group = new THREE.Group();
      group.position.set(x, y, z);
      const sphereGeo = new THREE.SphereGeometry(0.09, 16, 16);
      const sphereMat = new THREE.MeshBasicMaterial({ color: labelColor });
      const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
      group.add(sphereMesh);
      return group;
    };

    motorGroup.add(createSensorMarker(0, 1.25, 0, 0x38bdf8));    // Current Sensor (Top Box)
    motorGroup.add(createSensorMarker(0.5, 0.9, 0.4, 0xef4444));  // Temp Sensor (Body)
    motorGroup.add(createSensorMarker(-0.6, 0.9, 0, 0xf59e0b));   // Vibration Sensor (Bearing End)
    motorGroup.add(createSensorMarker(1.3, 0.3, 0, 0x10b981));    // Speed Sensor (Shaft)

    // Ground Grid
    const gridHelper = new THREE.GridHelper(10, 20, 0x334155, 0x1e293b);
    gridHelper.position.y = -0.8;
    scene.add(gridHelper);

    // 5. Animation Frame Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const current = telemetryRef.current;

      // A. Shaft & Fan Rotation based on RPM
      const rotationSpeed = (current.rpm / 60.0) * Math.PI * 2 * delta;
      if (shaftRef.current) {
        shaftRef.current.rotation.x += rotationSpeed;
      }
      if (fanRef.current) {
        fanRef.current.rotation.x += rotationSpeed;
      }

      // B. Thermal Material Color Interpolation based on Temperature
      if (statorMeshRef.current) {
        const temp = current.temp;
        const color = new THREE.Color();
        if (temp > 85.0) {
          color.setHex(0xef4444); // Critical Red
        } else if (temp > 65.0) {
          const ratio = (temp - 65.0) / 20.0;
          color.lerpColors(new THREE.Color(0x0284c7), new THREE.Color(0xf59e0b), ratio);
        } else {
          color.setHex(0x0284c7); // Normal Blue
        }
        statorMeshRef.current.material.color.copy(color);
      }

      // C. Mechanical Vibration Wobble Displacement based on RMS Vibration
      if (motorGroupRef.current) {
        const vibIntensity = Math.min(current.vib, 15.0);
        if (vibIntensity > 1.5) {
          const wobbleX = (Math.random() - 0.5) * (vibIntensity * 0.003);
          const wobbleY = (Math.random() - 0.5) * (vibIntensity * 0.003);
          const wobbleZ = (Math.random() - 0.5) * (vibIntensity * 0.003);
          motorGroupRef.current.position.set(wobbleX, wobbleY, wobbleZ);
        } else {
          motorGroupRef.current.position.set(0, 0, 0);
        }
      }

      // Slow orbital camera rotation
      motorGroup.rotation.y += 0.002;

      renderer.render(scene, camera);
    };

    animate();

    // Handle Resize
    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  const state = telemetry?.operating_state || 'NORMAL';
  const getStateBadge = () => {
    switch (state) {
      case 'OVERHEATING':
        return <span className="industrial-badge bg-amber-500/20 text-amber-400 border border-amber-500/30">🔥 OVERHEATING FAULT</span>;
      case 'BEARING_WEAR':
        return <span className="industrial-badge bg-amber-500/20 text-amber-300 border border-amber-500/30">⚙️ BEARING WEAR</span>;
      case 'ELECTRICAL_FAULT':
        return <span className="industrial-badge bg-rose-500/20 text-rose-400 border border-rose-500/30">⚡ ELECTRICAL FAULT</span>;
      default:
        return <span className="industrial-badge bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">✅ NORMAL OPERATION</span>;
    }
  };

  return (
    <div className="industrial-card relative h-[420px] flex flex-col justify-between overflow-hidden">
      
      {/* 3D Model View Overlay Banner */}
      <div className="flex items-center justify-between z-10">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span>DIGITAL TWIN 3D MODEL</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono">Live Physics Simulation Sync</p>
        </div>
        {getStateBadge()}
      </div>

      {/* 3D Canvas Container */}
      <div ref={mountRef} className="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Sensor Key Legend */}
      <div className="z-10 bg-slate-900/80 backdrop-blur-md p-2.5 rounded-lg border border-slate-800 text-xs flex flex-wrap gap-4 items-center justify-between text-slate-300">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
          <span>Current Sensor</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
          <span>Temp Sensor</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
          <span>Vibration Sensor</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          <span>Speed Sensor</span>
        </div>
      </div>
    </div>
  );
}
