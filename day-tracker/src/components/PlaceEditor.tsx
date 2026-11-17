import React, { useEffect, useRef, useState } from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import MapView, { Circle, Marker } from 'react-native-maps';
import * as Location from 'expo-location';
import { listPlaces, PlaceKind, savePlace, Place } from '../db';
import { nearbyCandidates, relabelVisits } from '../places';
import { Body, Button, Chip, Input, Sub, useTheme } from '../ui';

/** What size of area to remember. A street or neighbourhood needs a much bigger circle than a shop. */
const SIZES = [
  { r: 75, label: '📍 Exact spot' },
  { r: 150, label: '🏢 Building' },
  { r: 300, label: '🏘️ Block / campus' },
  { r: 500, label: '🛣️ Street / area' },
];
const KINDS: { k: PlaceKind; label: string }[] = [
  { k: 'home', label: '🏠 Home' }, { k: 'office', label: '🏢 Office' }, { k: 'other', label: '⭐ Other' },
];
const DEFAULT_NAME: Record<PlaceKind, string> = { home: 'Home', office: 'Office', other: '' };

type Coord = { latitude: number; longitude: number };

/**
 * Remember a place: current location, a typed address/street, or a dragged pin.
 * Choose Home / Office / Other, give it a name (with suggestions), choose how big it is.
 */
export function PlaceEditor({ kind: initialKind, initial, at, allowKindChange, onSaved, onSkip }: {
  kind: PlaceKind; initial?: Place; at?: Coord & { name?: string | null; address?: string | null };
  allowKindChange?: boolean; onSaved: (id: number) => void; onSkip?: () => void;
}) {
  const t = useTheme();
  const map = useRef<MapView>(null);
  const [kind, setKind] = useState<PlaceKind>(initial?.kind ?? initialKind);
  const [name, setName] = useState(initial?.name ?? at?.name ?? DEFAULT_NAME[initialKind]);
  const [coord, setCoord] = useState<Coord | null>(
    initial ? { latitude: initial.lat, longitude: initial.lon } : at ? { latitude: at.latitude, longitude: at.longitude } : null);
  const [address, setAddress] = useState(initial?.address ?? at?.address ?? '');
  const [street, setStreet] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [radius, setRadius] = useState(initial?.radius ?? (initialKind === 'other' ? 100 : 150));
  const [query, setQuery] = useState('');
  const [busy, setBusy] = useState<'gps' | 'search' | null>(null);

  useEffect(() => {
    if (initial) return;
    if (at) moveTo(at, false); else useCurrent();
  }, []);

  const moveTo = async (c: Coord, animate = true) => {
    setCoord(c);
    if (animate) map.current?.animateToRegion({ ...c, latitudeDelta: 0.006, longitudeDelta: 0.006 }, 400);
    try {
      const [r] = await Location.reverseGeocodeAsync(c);
      if (r) {
        setAddress(r.formattedAddress ?? [r.name, r.street, r.district, r.city].filter(Boolean).join(', '));
        setStreet(r.street ?? r.district ?? null);
      }
    } catch {}
    nearbyCandidates({ lat: c.latitude, lon: c.longitude }, 60).then((cs) => setSuggestions(cs.slice(0, 4).map((x) => x.name)));
  };

  async function useCurrent() {
    setBusy('gps');
    try {
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Highest });
      await moveTo({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
    } catch {
      Alert.alert('Location unavailable', 'Make sure location is turned on, or search for the address instead.');
    } finally { setBusy(null); }
  }

  async function search() {
    const q = query.trim();
    if (!q) return;
    setBusy('search');
    try {
      const [r] = await Location.geocodeAsync(q);
      if (!r) { Alert.alert('Not found', 'Try adding the area or city, e.g. “Anna Salai, Chennai”.'); return; }
      await moveTo({ latitude: r.latitude, longitude: r.longitude });
      // Typing a bare street name usually means "remember this street".
      if (!/\d/.test(q) && radius < 300) setRadius(500);
      if (!name.trim() && kind === 'other') setName(q.split(',')[0]);
    } catch {
      Alert.alert('Search failed', 'Check your internet connection and try again.');
    } finally { setBusy(null); }
  }

  function changeKind(k: PlaceKind) {
    setKind(k);
    if (!name.trim() || Object.values(DEFAULT_NAME).includes(name)) setName(DEFAULT_NAME[k]);
  }

  function save() {
    if (!coord) return;
    const finalName = name.trim() || street || 'My place';
    const doSave = () => {
      const id = savePlace({ id: initial?.id, name: finalName, kind, lat: coord.latitude, lon: coord.longitude, radius, address: address || null });
      const saved = listPlaces().find((p) => p.id === id);
      if (saved) relabelVisits(saved);
      onSaved(id);
    };
    const existing = kind !== 'other' && !initial ? listPlaces().find((p) => p.kind === kind) : undefined;
    if (existing) {
      Alert.alert(`Replace your ${DEFAULT_NAME[kind]}?`, `“${existing.name}” will be moved to this location.`,
        [{ text: 'Cancel' }, { text: 'Replace', onPress: doSave }]);
    } else doSave();
  }

  const nameIdeas = [...new Set([street, ...suggestions].filter((x): x is string => !!x && x !== name))];

  return (
    <View>
      <View style={[s.mapWrap, { borderColor: t.border }]}>
        <MapView
          ref={map}
          style={StyleSheet.absoluteFill}
          showsUserLocation
          initialRegion={coord ? { ...coord, latitudeDelta: 0.006, longitudeDelta: 0.006 } : undefined}
          onLongPress={(e) => moveTo(e.nativeEvent.coordinate)}>
          {coord && (
            <>
              <Marker coordinate={coord} draggable onDragEnd={(e) => moveTo(e.nativeEvent.coordinate)} pinColor={t.accent} />
              <Circle center={coord} radius={radius} strokeColor={t.accent} fillColor="rgba(37,99,235,0.15)" />
            </>
          )}
        </MapView>
      </View>
      <Sub style={{ marginTop: 6 }}>Drag the pin or long-press the map to fine-tune.</Sub>
      {address ? <Body style={{ marginTop: 6 }}>{address}</Body> : null}

      <Button title="📍 Use where I am now" kind="secondary" busy={busy === 'gps'} onPress={useCurrent} />
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        <Input style={{ flex: 1 }} placeholder="…or type an address or street" value={query} onChangeText={setQuery}
          onSubmitEditing={search} returnKeyType="search" />
        <Button title="Find" kind="secondary" busy={busy === 'search'} onPress={search} style={{ marginTop: 8 }} />
      </View>

      {allowKindChange && (
        <>
          <Sub style={{ marginTop: 14, marginBottom: 6 }}>Remember as</Sub>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
            {KINDS.map((x) => <Chip key={x.k} label={x.label} active={kind === x.k} onPress={() => changeKind(x.k)} />)}
          </View>
        </>
      )}

      <Input placeholder="Name (e.g. Mom’s house, Gym, Anna Salai)" value={name} onChangeText={setName} />
      {nameIdeas.length > 0 && (
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 8 }}>
          {nameIdeas.slice(0, 5).map((n) => <Chip key={n} label={n} onPress={() => setName(n)} />)}
        </View>
      )}

      <Sub style={{ marginTop: 12, marginBottom: 6 }}>What are you remembering?</Sub>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
        {SIZES.map((x) => <Chip key={x.r} label={x.label} active={radius === x.r} onPress={() => setRadius(x.r)} />)}
      </View>
      <Sub>You’ll count as “at {name.trim() || 'this place'}” anywhere inside the blue circle ({radius} m).</Sub>

      <Button title={`Remember ${name.trim() || 'this place'}`} disabled={!coord} onPress={save} />
      {onSkip ? <Button title="Skip for now" kind="secondary" onPress={onSkip} /> : null}
    </View>
  );
}

const s = StyleSheet.create({
  mapWrap: { height: 260, borderRadius: 16, overflow: 'hidden', borderWidth: StyleSheet.hairlineWidth },
});
