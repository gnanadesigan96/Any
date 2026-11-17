import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, View } from 'react-native';
import { getVisit, pointsBetween, renameVisit, setTripMode, Trip, Visit, db } from '../db';
import { PlaceEditor } from './PlaceEditor';
import { Candidate, categoryIcon, nearbyCandidates } from '../places';
import { formatDistance, formatDuration, formatTime, MODE_LABEL } from '../geo';
import { emitChange } from '../events';
import { RouteMap } from './RouteMap';
import { Body, Button, Card, Chip, H1, H2, Input, Sub, useTheme } from '../ui';

function Sheet({ visible, onClose, children }: { visible: boolean; onClose: () => void; children: React.ReactNode }) {
  const t = useTheme();
  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <ScrollView style={{ backgroundColor: t.bg }} contentContainerStyle={{ padding: 20, paddingBottom: 48 }} keyboardShouldPersistTaps="handled">
        <Pressable onPress={onClose} hitSlop={12} style={{ alignSelf: 'flex-end', marginBottom: 8 }}>
          <Body style={{ color: t.accent, fontWeight: '700' }}>Done</Body>
        </Pressable>
        {children}
      </ScrollView>
    </Modal>
  );
}

/** "Remember this place": where you are now, or a given spot (e.g. a past visit). */
export function RememberSheet({ visible, at, onClose }: {
  visible: boolean; at?: { latitude: number; longitude: number; name?: string | null; address?: string | null }; onClose: () => void;
}) {
  if (!visible) return null;
  return (
    <Sheet visible onClose={onClose}>
      <H1>📌 Remember this place</H1>
      <Sub style={{ marginBottom: 12 }}>Save it as Home, Office or any named place — a single shop, a building, or a whole street.
        From now on (and in your past days) it shows up by this name.</Sub>
      <PlaceEditor kind="other" allowKindChange at={at} onSaved={() => { emitChange(); onClose(); }} />
    </Sheet>
  );
}

/** Details of a stop: when, how long, and "is this the right place?" */
export function VisitSheet({ visit, onClose }: { visit: Visit | null; onClose: () => void }) {
  const t = useTheme();
  const [cands, setCands] = useState<Candidate[] | null>(null);
  const [custom, setCustom] = useState('');
  const [remember, setRemember] = useState(false);

  useEffect(() => {
    setCands(null); setCustom(''); setRemember(false);
    if (visit) nearbyCandidates({ lat: visit.lat, lon: visit.lon }, 120).then(setCands);
  }, [visit?.id]);

  if (!visit) return null;
  const end = visit.end_ts ?? Date.now();

  const choose = (name: string, category?: string) => {
    renameVisit(visit.id, name);
    if (category) db.runSync('UPDATE visits SET category=? WHERE id=?', category, visit.id);
    emitChange(); onClose();
  };
  if (remember) {
    return <RememberSheet visible at={{ latitude: visit.lat, longitude: visit.lon, name: custom.trim() || visit.name, address: visit.address }}
      onClose={onClose} />;
  }

  return (
    <Sheet visible onClose={onClose}>
      <H1>{categoryIcon(visit.category)} {visit.name ?? 'Unknown place'}</H1>
      {visit.address ? <Sub>{visit.address}</Sub> : null}
      <Card style={{ marginTop: 16 }}>
        <Body>Arrived {formatTime(visit.start_ts)}{visit.end_ts ? ` · Left ${formatTime(visit.end_ts)}` : ' · Still here'}</Body>
        <Body style={{ fontWeight: '700', marginTop: 4 }}>{formatDuration(end - visit.start_ts)}</Body>
      </Card>
      <RouteMap points={[]} visits={[visit]} style={{ height: 200, marginBottom: 12 }} />

      <H2 style={{ marginTop: 8 }}>Is this the right place?</H2>
      {cands == null ? <ActivityIndicator color={t.accent} /> :
        cands.length === 0 ? <Sub>No named places found nearby. Type a name below.</Sub> :
          cands.slice(0, 8).map((c) => (
            <Pressable key={c.name} onPress={() => choose(c.name, c.category)}
              style={{ paddingVertical: 12, borderBottomWidth: 1, borderColor: t.border }}>
              <Body>{categoryIcon(c.category)} {c.name}</Body>
              <Sub>{c.category.replace(/_/g, ' ')} · {Math.round(c.distance)} m away</Sub>
            </Pressable>
          ))}
      <Input placeholder="Or type a name (e.g. Mom's house, Gym)" value={custom} onChangeText={setCustom} />
      <Button title="Use this name" disabled={!custom.trim()} onPress={() => choose(custom.trim())} />
      <Button title="📌 Remember this place (Home, Office, favourite…)" kind="secondary" onPress={() => setRemember(true)} />
    </Sheet>
  );
}

const MODES = ['walk', 'run', 'cycle', 'bike', 'vehicle', 'bus', 'train', 'flight'];

/** Details of a journey: route on the map, times, distance, speed and travel mode. */
export function TripSheet({ trip, onClose }: { trip: Trip | null; onClose: () => void }) {
  const [mode, setMode] = useState(trip?.mode ?? 'vehicle');
  useEffect(() => setMode(trip?.mode ?? 'vehicle'), [trip?.id]);
  if (!trip) return null;
  const end = trip.end_ts ?? Date.now();
  const pts = pointsBetween(trip.start_ts, end);
  const from = getVisit(trip.from_visit);
  const to = getVisit(trip.to_visit);
  const ms = end - trip.start_ts;
  const kmh = ms > 0 ? trip.distance_m / 1000 / (ms / 3600000) : 0;
  const maxKmh = Math.max(0, ...pts.map((p) => (p.speed ?? 0) * 3.6));

  return (
    <Sheet visible onClose={onClose}>
      <H1>{MODE_LABEL[mode] ?? mode}</H1>
      <Sub>{from?.name ?? from?.address ?? 'Start'}  →  {to?.name ?? to?.address ?? (trip.end_ts ? 'Destination' : 'On the way…')}</Sub>
      <RouteMap points={pts} visits={[from, to].filter(Boolean) as Visit[]} style={{ marginTop: 16, marginBottom: 12 }} />
      <Card>
        <Row k="Left" v={formatTime(trip.start_ts)} />
        <Row k="Arrived" v={trip.end_ts ? formatTime(trip.end_ts) : '—'} />
        <Row k="Travel time" v={formatDuration(ms)} />
        <Row k="Distance" v={formatDistance(trip.distance_m)} />
        <Row k="Average speed" v={`${kmh.toFixed(1)} km/h`} />
        <Row k="Top speed" v={`${maxKmh.toFixed(0)} km/h`} />
        <Row k="GPS points" v={String(pts.length)} />
      </Card>
      <H2>How did you travel?</H2>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
        {MODES.map((m) => (
          <Chip key={m} label={MODE_LABEL[m]} active={mode === m}
            onPress={() => { setMode(m); setTripMode(trip.id, m); emitChange(); }} />
        ))}
      </View>
    </Sheet>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  const t = useTheme();
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6 }}>
      <Body style={{ color: t.sub }}>{k}</Body><Body style={{ fontWeight: '700' }}>{v}</Body>
    </View>
  );
}
