import React, { useRef, useEffect, useState, useMemo } from 'react';
import { View, Text, Dimensions, TouchableOpacity } from 'react-native';
import { GLView } from 'expo-gl';
import { Renderer } from 'expo-three';
import * as THREE from 'three';
import { Gyroscope } from 'expo-sensors';
import { Asset } from 'expo-asset';
import { loadAsync } from 'expo-three';
import BottomSheet from '@gorhom/bottom-sheet';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

function convertRADecToXYZ(ra, dec, radius = 28.5) {
  const raRad = (ra / 180) * Math.PI;
  const decRad = (dec / 180) * Math.PI;

  const x = radius * Math.cos(decRad) * Math.cos(raRad);
  const y = radius * Math.sin(decRad);
  const z = radius * Math.cos(decRad) * Math.sin(raRad);

  return { x, y, z };
}

export default function StarMapScreen() {
  const rotationRef = useRef({ x: 0, y: 0 });
  const angleRef = useRef({ x: 0, y: 0 });
  const raycaster = useRef(new THREE.Raycaster());
  const mouse = useRef(new THREE.Vector2());
  const starsRef = useRef([]);
  const cameraRef = useRef(null);
  const glViewDimensions = useRef({ width: 0, height: 0 });

  const [selectedStar, setSelectedStar] = useState(null);
  const bottomSheetRef = useRef(null);
  const snapPoints = useMemo(() => ['25%', '50%'], []);

  useEffect(() => {
    Gyroscope.setUpdateInterval(50);
    const sub = Gyroscope.addListener(({ x, y }) => {
      angleRef.current.x += x * 0.03;
      angleRef.current.y += y * 0.03;

      rotationRef.current = {
        x: angleRef.current.x + THREE.MathUtils.degToRad(-30),
        y: angleRef.current.y,
      };
    });

    return () => sub.remove();
  }, []);

  const handleTouch = (event) => {
    if (!cameraRef.current || glViewDimensions.current.width === 0) {
      console.warn("카메라 또는 GLView 크기가 초기화되지 않아 터치 감지가 불가능합니다.");
      return;
    }

    const { locationX, locationY } = event.nativeEvent;

    mouse.current.x = (locationX / glViewDimensions.current.width) * 2 - 1;
    mouse.current.y = -(locationY / glViewDimensions.current.height) * 2 + 1;

    console.log(`터치: (${locationX}, ${locationY}) -> 정규화된 좌표: (${mouse.current.x.toFixed(2)}, ${mouse.current.y.toFixed(2)})`);

    raycaster.current.setFromCamera(mouse.current, cameraRef.current);

    const intersectableObjects = starsRef.current;
    const intersects = raycaster.current.intersectObjects(intersectableObjects);

    console.log("교차된 객체 수:", intersects.length);
    if (intersects.length > 0) {
      console.log("첫 번째 교차 객체 데이터:", intersects[0].object.userData);
    }

    if (intersects.length > 0) {
      const star = intersects[0].object.userData;
      setSelectedStar(star);
      bottomSheetRef.current?.expand();
    } else {
      setSelectedStar(null);
      bottomSheetRef.current?.close();
    }
  };


  return (
    <View style={{ flex: 1 }}>
      <GLView
        style={{ flex: 1 }}
        onContextCreate={async (gl) => {
          const { drawingBufferWidth: width, drawingBufferHeight: height } = gl;

          glViewDimensions.current = { width, height };

          const scene = new THREE.Scene();

          const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
          // 수정된 부분: 카메라의 Z축 위치를 별들이 생성되는 범위에 가깝게 조정
          camera.position.z = 25; // 별들이 28.5m 거리에 있으므로, 카메라를 25m로 이동
          camera.position.y = -0.1;

          cameraRef.current = camera;

          const renderer = new Renderer({ gl });
          renderer.setSize(width, height);

          const asset = Asset.fromModule(require('../../assets/textures/starsky2.jpg'));
          await asset.downloadAsync();
          const texture = await loadAsync(asset);

          const starData = require('../../assets/data/star_data.json');

          const starGroup = new THREE.Group();
          // GLView onContextCreate 함수 내부의 starData.forEach 루프 안
          starData.forEach((starInfo) => {
            // 여기를 수정하세요! 별의 반지름을 5.0으로 대폭 늘려서 테스트
            const starRadius = 5.0; // 현재 0.5였던 것을 5.0으로 변경

            const { x, y, z } = convertRADecToXYZ(starInfo.ra, starInfo.dec, 28.5);

            const starGeo = new THREE.SphereGeometry(starRadius, 8, 8);
            const starMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const starMesh = new THREE.Mesh(starGeo, starMat);
            starMesh.position.set(x, y, z);
            starMesh.userData = {
              name: starInfo.name || 'Unknown',
              type: starInfo.type || 'Star',
              ra: starInfo.ra,
              dec: starInfo.dec,
            };
            starGroup.add(starMesh);
            starsRef.current.push(starMesh);

          });
          scene.add(starGroup);

          const geometry = new THREE.SphereGeometry(30, 64, 64);
          const material = new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.BackSide,
          });
          const sphere = new THREE.Mesh(geometry, material);
          scene.add(sphere);

          const animate = () => {
            requestAnimationFrame(animate);

            if (cameraRef.current) {
              cameraRef.current.rotation.x = rotationRef.current.x;
              cameraRef.current.rotation.y = rotationRef.current.y;
            }

            renderer.render(scene, camera);
            gl.endFrameEXP();
          };

          animate();
        }}
        onTouchStart={handleTouch}
      />

      <TouchableOpacity
        style={{ position: 'absolute', top: 50, left: 20, backgroundColor: 'blue', padding: 10, borderRadius: 5 }}
        onPress={() => {
          setSelectedStar({ name: "테스트 별", type: "테스트" }); // 임시 데이터 설정
          bottomSheetRef.current?.expand();
          console.log("바텀시트 expand 시도");
        }}
      >
        <Text style={{ color: 'white' }}>바텀시트 열기 테스트</Text>
      </TouchableOpacity>

      {/* 바텀시트 구현 */}
      <BottomSheet
        ref={bottomSheetRef}
        index={-1}
        snapPoints={snapPoints}
        enablePanOnContent={false}
      >
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          {selectedStar ? (
            <>
              <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 10 }}>{selectedStar.name}</Text>
              <Text style={{ fontSize: 16 }}>유형: {selectedStar.type}</Text>
              {selectedStar.ra && selectedStar.dec && (
                <>
                  <Text style={{ fontSize: 16 }}>적경 (RA): {selectedStar.ra.toFixed(2)}</Text>
                  <Text style={{ fontSize: 16 }}>적위 (Dec): {selectedStar.dec.toFixed(2)}</Text>
                </>
              )}
            </>
          ) : (
            <Text style={{ fontSize: 18, color: 'gray' }}>선택된 별이 없습니다.</Text>
          )}
        </View>
      </BottomSheet>
    </View>
  );
}
