import React, { useEffect, useRef } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import { Point, Visit } from '../db';
import { categoryIcon } from '../places';
import { useTheme } from '../ui';

/** Map of a route (GPS points) plus place markers, zoomed to fit. */
export function RouteMap({ points, visits = [], style, live }: { points: Point[]; visits?: Visit[]; style?: ViewStyle; live?: boolean }) {
  const t = useTheme();
  const ref = useRef<MapView>(null);
  const coords = points.map((p) => ({ latitude: p.lat, longitude: p.lon }));
  const all = [...coords, ...visits.map((v) => ({ latitude: v.lat, longitude: v.lon }))];

  useEffect(() => {
    if (!all.length) return;
    const id = setTimeout(() => ref.current?.fitToCoordinates(all, {
      edgePadding: { top: 60, right: 50, bottom: 60, left: 50 }, animated: true }), 300);
    return () => clearTimeout(id);
  }, [points.length, visits.length]);

  const first = all[0];
  return (
    <View style={[s.wrap, { borderColor: t.border }, style]}>
      <MapView ref={ref} style={StyleSheet.absoluteFill} showsUserLocation={live}
        initialRegion={first ? { ...first, latitudeDelta: 0.05, longitudeDelta: 0.05 } : undefined}>
        {coords.length > 1 && <Polyline coordinates={coords} strokeColor={t.accent} strokeWidth={5} />}
        {coords.length > 1 && !visits.length && (
          <>
            <Marker coordinate={coords[0]} title="Start" pinColor="green" />
            <Marker coordinate={coords[coords.length - 1]} title="End" pinColor="red" />
          </>
        )}
        {visits.map((v) => (
          <Marker key={v.id} coordinate={{ latitude: v.lat, longitude: v.lon }}
            title={`${categoryIcon(v.category)} ${v.name ?? v.address ?? 'Visit'}`} description={v.address ?? undefined} />
        ))}
      </MapView>
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { borderRadius: 16, overflow: 'hidden', borderWidth: StyleSheet.hairlineWidth, height: 280 },
});
