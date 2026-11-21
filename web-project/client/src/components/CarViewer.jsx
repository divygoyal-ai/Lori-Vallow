import { Suspense, useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, Lightformer, ContactShadows, RoundedBox, useGLTF, Float } from '@react-three/drei';
import * as THREE from 'three';

// Stylised procedural car — placeholder used until a real GLB is uploaded for a model.
function ProceduralCar({ color, doorsOpen, lights }) {
  const paint = { color, metalness: 0.9, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05 };
  const glass = { color: '#0a0c10', metalness: 1, roughness: 0.05, transparent: true, opacity: 0.85 };
  const wheel = (x, z) => (
    <group position={[x, 0.36, z]} rotation={[0, 0, Math.PI / 2]}>
      <mesh><cylinderGeometry args={[0.36, 0.36, 0.28, 40]} /><meshStandardMaterial color="#111" roughness={0.8} /></mesh>
      <mesh position={[0, x > 0 ? 0.145 : -0.145, 0]}><cylinderGeometry args={[0.24, 0.24, 0.02, 32]} /><meshStandardMaterial color="#b8b8bd" metalness={1} roughness={0.2} /></mesh>
    </group>
  );
  return (
    <group>
      <RoundedBox args={[1.9, 0.42, 4.4]} radius={0.18} smoothness={6} position={[0, 0.58, 0]}><meshPhysicalMaterial {...paint} /></RoundedBox>
      <RoundedBox args={[1.6, 0.14, 1.5]} radius={0.06} position={[0, 0.84, 1.2]} rotation={[-0.06, 0, 0]}><meshPhysicalMaterial {...paint} /></RoundedBox>
      <RoundedBox args={[1.5, 0.42, 1.9]} radius={0.18} smoothness={6} position={[0, 1.02, -0.2]}><meshPhysicalMaterial {...glass} /></RoundedBox>
      <RoundedBox args={[1.42, 0.06, 1.6]} radius={0.03} position={[0, 1.26, -0.2]}><meshPhysicalMaterial {...paint} /></RoundedBox>
      <group position={[0.96, 0.7, 0.2]} rotation={[0, doorsOpen ? -0.9 : 0, 0]}>
        <mesh position={[0, 0, 0.5]}><boxGeometry args={[0.03, 0.3, 1.0]} /><meshPhysicalMaterial {...paint} /></mesh>
      </group>
      <group position={[-0.96, 0.7, 0.2]} rotation={[0, doorsOpen ? 0.9 : 0, 0]}>
        <mesh position={[0, 0, 0.5]}><boxGeometry args={[0.03, 0.3, 1.0]} /><meshPhysicalMaterial {...paint} /></mesh>
      </group>
      {[[-0.6, 2.2], [0.6, 2.2]].map(([x, z]) => (
        <mesh key={x} position={[x, 0.68, z]}><boxGeometry args={[0.45, 0.06, 0.05]} />
          <meshStandardMaterial color={lights ? '#fff6d0' : '#222'} emissive={lights ? '#fff2c0' : '#000'} emissiveIntensity={lights ? 3 : 0} /></mesh>
      ))}
      {[[-0.6, -2.2], [0.6, -2.2]].map(([x, z]) => (
        <mesh key={x} position={[x, 0.7, z]}><boxGeometry args={[0.5, 0.05, 0.05]} /><meshStandardMaterial color="#a00" emissive="#f00" emissiveIntensity={lights ? 2.5 : 0.4} /></mesh>
      ))}
      {wheel(0.95, 1.4)}{wheel(-0.95, 1.4)}{wheel(0.95, -1.4)}{wheel(-0.95, -1.4)}
      {/* interior seats, visible through the glass */}
      <RoundedBox args={[0.5, 0.3, 0.3]} radius={0.06} position={[-0.38, 0.95, 0.1]}><meshStandardMaterial color="#6b4a2f" roughness={0.6} /></RoundedBox>
      <RoundedBox args={[0.5, 0.3, 0.3]} radius={0.06} position={[0.38, 0.95, 0.1]}><meshStandardMaterial color="#6b4a2f" roughness={0.6} /></RoundedBox>
    </group>
  );
}

function GlbCar({ url, color }) {
  const { scene } = useGLTF(url);
  useEffect(() => {
    scene.traverse((o) => {
      if (o.isMesh && /body|paint|carpaint/i.test(o.material?.name || '')) {
        o.material = o.material.clone();
        o.material.color = new THREE.Color(color);
      }
    });
  }, [scene, color]);
  return <primitive object={scene} />;
}

// Smoothly moves the camera between the exterior orbit and a seat-level interior view.
function CameraRig({ view, controls }) {
  const { camera } = useThree();
  const target = useRef(new THREE.Vector3());
  useFrame(() => {
    const inside = view === 'interior';
    const pos = inside ? new THREE.Vector3(-0.38, 1.0, -0.15) : new THREE.Vector3(5.5, 1.8, 5.5);
    const look = inside ? new THREE.Vector3(-0.38, 0.95, 3) : new THREE.Vector3(0, 0.7, 0);
    if (!controls.current) return;
    if (inside || camera.userData.transition) {
      camera.position.lerp(pos, 0.06);
      target.current.lerp(look, 0.06);
      controls.current.target.copy(target.current);
      camera.userData.transition = camera.position.distanceTo(pos) > 0.05;
    }
  });
  useEffect(() => { camera.userData.transition = true; }, [view, camera]);
  return null;
}

export default function CarViewer({ color = '#b30000', modelUrl, view = 'exterior', doorsOpen, lights, autoRotate = true, hero }) {
  const controls = useRef();
  return (
    <Canvas shadows camera={{ position: [5.5, 1.8, 5.5], fov: hero ? 38 : 45 }} dpr={[1, 2]}>
      <color attach="background" args={['#08080a']} />
      <fog attach="fog" args={['#08080a', 10, 24]} />
      <Suspense fallback={null}>
        <Environment resolution={256}>
          <Lightformer form="rect" intensity={4} position={[0, 5, -4]} scale={[12, 3, 1]} />
          <Lightformer form="rect" intensity={2.5} position={[-6, 1, 2]} rotation-y={Math.PI / 2} scale={[8, 2, 1]} />
          <Lightformer form="rect" intensity={2.5} position={[6, 1, 2]} rotation-y={-Math.PI / 2} scale={[8, 2, 1]} />
          <Lightformer form="ring" color="#c9a96a" intensity={3} position={[0, 3, 5]} scale={4} />
        </Environment>
        <Float speed={hero ? 1.2 : 0} rotationIntensity={0} floatIntensity={hero ? 0.4 : 0}>
          {modelUrl ? <GlbCar url={modelUrl} color={color} /> : <ProceduralCar color={color} doorsOpen={doorsOpen} lights={lights} />}
        </Float>
        <ContactShadows position={[0, 0, 0]} opacity={0.7} scale={14} blur={2.6} far={4} />
        <mesh rotation-x={-Math.PI / 2} position={[0, -0.01, 0]}><circleGeometry args={[9, 64]} /><meshStandardMaterial color="#0d0d10" metalness={0.8} roughness={0.35} /></mesh>
      </Suspense>
      <OrbitControls ref={controls} enablePan={false} enableZoom={!hero} minDistance={view === 'interior' ? 0.1 : 3.5} maxDistance={10}
        maxPolarAngle={view === 'interior' ? Math.PI : Math.PI / 2 - 0.05} autoRotate={autoRotate && view === 'exterior'} autoRotateSpeed={hero ? 0.9 : 1.4} />
      <CameraRig view={view} controls={controls} />
    </Canvas>
  );
}
