import React, { useEffect, useMemo, useRef } from 'react';
import { StyleSheet, Text, useColorScheme, View, ViewStyle } from 'react-native';
import { Camera, CameraRef, GeoJSONSource, Layer, Map, UserLocation, ViewAnnotation } from '@maplibre/maplibre-react-native';
import { useTheme } from '../ui';

/**
 * Day Tracker's own map. It's drawn on the phone by MapLibre (open source) from OpenStreetMap data
 * served free by OpenFreeMap: no Google, no API key, no cost. Routes, pins and circles are our own layers.
 */
const STYLE_LIGHT = 'https://tiles.openfreemap.org/styles/liberty';
const STYLE_DARK = 'https://tiles.openfreemap.org/styles/dark';

export interface MapPin { id: string; lat: number; lon: number; icon: string; label?: string }
type LatLng = { latitude: number; longitude: number };

export function AppMap({ route = [], pins = [], circle, dragPin, onDragPin, onLongPress, live, style, zoom = 15 }: {
  route?: { lat: number; lon: number }[];
  pins?: MapPin[];
  circle?: { lat: number; lon: number; radius: number };
  /** A single movable pin (place editor). */
  dragPin?: LatLng | null;
  onDragPin?: (c: LatLng) => void;
  onLongPress?: (c: LatLng) => void;
  live?: boolean;
  style?: ViewStyle;
  zoom?: number;
}) {
  const t = useTheme();
  const dark = useColorScheme() === 'dark';
  const cam = useRef<CameraRef>(null);

  const all = useMemo(() => [
    ...route,
    ...pins,
    ...(dragPin ? [{ lat: dragPin.latitude, lon: dragPin.longitude }] : []),
  ], [route, pins, dragPin]);

  // Zoom to fit everything we draw (or follow the single pin).
  const fitKey = `${route.length}|${pins.map((p) => p.id).join(',')}|${dragPin?.latitude.toFixed(5)},${dragPin?.longitude.toFixed(5)}|${circle?.radius}`;
  useEffect(() => {
    if (!all.length) return;
    const id = setTimeout(() => {
      if (all.length === 1 || dragPin) {
        const p = dragPin ? { lat: dragPin.latitude, lon: dragPin.longitude } : all[0];
        cam.current?.easeTo({ center: [p.lon, p.lat], zoom: circle && circle.radius > 250 ? 14.5 : zoom, duration: 500 });
      } else {
        const lons = all.map((p) => p.lon), lats = all.map((p) => p.lat);
        cam.current?.fitBounds([Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)],
          { padding: { top: 60, right: 50, bottom: 60, left: 50 }, duration: 600 });
      }
    }, 250);
    return () => clearTimeout(id);
  }, [fitKey]);

  const first = all[0];
  const routeGeo = useMemo<GeoJSON.Feature>(() => ({
    type: 'Feature', properties: {},
    geometry: { type: 'LineString', coordinates: route.map((p) => [p.lon, p.lat]) },
  }), [route]);
  const endsGeo = useMemo<GeoJSON.FeatureCollection>(() => ({
    type: 'FeatureCollection',
    features: route.length > 1 ? [
      { type: 'Feature', properties: { kind: 'start' }, geometry: { type: 'Point', coordinates: [route[0].lon, route[0].lat] } },
      { type: 'Feature', properties: { kind: 'end' }, geometry: { type: 'Point', coordinates: [route[route.length - 1].lon, route[route.length - 1].lat] } },
    ] : [],
  }), [route]);
  const circleGeo = useMemo(() => (circle ? circlePolygon(circle.lat, circle.lon, circle.radius) : null), [circle?.lat, circle?.lon, circle?.radius]);

  return (
    <View style={[s.wrap, { borderColor: t.border }, style]}>
      <Map
        style={StyleSheet.absoluteFill}
        mapStyle={dark ? STYLE_DARK : STYLE_LIGHT}
        logo={false}
        attribution
        attributionPosition={{ bottom: 6, right: 6 }}
        compass
        onLongPress={onLongPress ? (e) => onLongPress({ longitude: e.nativeEvent.lngLat[0], latitude: e.nativeEvent.lngLat[1] }) : undefined}>
        <Camera ref={cam} initialViewState={first ? { center: [first.lon, first.lat], zoom } : { center: [78.9629, 20.5937], zoom: 4 }} />

        {circleGeo && (
          <GeoJSONSource id="circle" data={circleGeo}>
            <Layer type="fill" id="circle-fill" style={{ fillColor: t.accent, fillOpacity: 0.15 }} />
            <Layer type="line" id="circle-line" style={{ lineColor: t.accent, lineWidth: 2 }} />
          </GeoJSONSource>
        )}

        {route.length > 1 && (
          <GeoJSONSource id="route" data={routeGeo}>
            <Layer type="line" id="route-casing" style={{ lineColor: dark ? '#0B1120' : '#FFFFFF', lineWidth: 9, lineCap: 'round', lineJoin: 'round' }} />
            <Layer type="line" id="route-line" style={{ lineColor: t.accent, lineWidth: 5, lineCap: 'round', lineJoin: 'round' }} />
          </GeoJSONSource>
        )}
        {route.length > 1 && !pins.length && (
          <GeoJSONSource id="ends" data={endsGeo}>
            <Layer type="circle" id="ends-dot" style={{
              circleRadius: 7, circleStrokeWidth: 3, circleStrokeColor: '#FFFFFF',
              circleColor: ['match', ['get', 'kind'], 'start', t.home, t.danger] as any,
            }} />
          </GeoJSONSource>
        )}

        {pins.map((p) => (
          <ViewAnnotation key={p.id} id={`pin-${p.id}`} lngLat={[p.lon, p.lat]} anchor="bottom" title={p.label}>
            <Pin icon={p.icon} color={t.card} border={t.accent} />
          </ViewAnnotation>
        ))}

        {dragPin && (
          <ViewAnnotation id="drag-pin" lngLat={[dragPin.longitude, dragPin.latitude]} anchor="bottom" draggable
            onDragEnd={(e) => onDragPin?.({ longitude: e.nativeEvent.lngLat[0], latitude: e.nativeEvent.lngLat[1] })}>
            <Pin icon="📍" color={t.accent} border="#FFFFFF" big />
          </ViewAnnotation>
        )}

        {live && <UserLocation accuracy heading />}
      </Map>
    </View>
  );
}

function Pin({ icon, color, border, big }: { icon: string; color: string; border: string; big?: boolean }) {
  const size = big ? 44 : 36;
  return (
    <View style={{ alignItems: 'center' }}>
      <View style={{ width: size, height: size, borderRadius: size / 2, backgroundColor: color, borderWidth: 2.5, borderColor: border,
        alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOpacity: 0.25, shadowRadius: 4, shadowOffset: { width: 0, height: 2 }, elevation: 4 }}>
        <Text style={{ fontSize: big ? 22 : 18 }}>{icon}</Text>
      </View>
      <View style={{ width: 0, height: 0, borderLeftWidth: 6, borderRightWidth: 6, borderTopWidth: 8,
        borderLeftColor: 'transparent', borderRightColor: 'transparent', borderTopColor: border }} />
    </View>
  );
}

/** A true-to-scale circle (radius in metres) as a polygon. */
function circlePolygon(lat: number, lon: number, radius: number): GeoJSON.Feature {
  const coords: number[][] = [];
  const dLat = radius / 111320;
  const dLon = radius / (111320 * Math.cos((lat * Math.PI) / 180));
  for (let i = 0; i <= 64; i++) {
    const a = (i / 64) * 2 * Math.PI;
    coords.push([lon + dLon * Math.cos(a), lat + dLat * Math.sin(a)]);
  }
  return { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [coords] } };
}

const s = StyleSheet.create({
  wrap: { borderRadius: 16, overflow: 'hidden', borderWidth: StyleSheet.hairlineWidth, height: 280 },
});
