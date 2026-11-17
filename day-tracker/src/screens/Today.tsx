import React, { useCallback, useEffect, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, View } from 'react-native';
import { Trip, Visit } from '../db';
import { summarizeDay, DaySummary, TimelineItem } from '../stats';
import { stepsBetween, StepResult } from '../steps';
import { formatDistance, formatDuration, formatTime, MODE_LABEL } from '../geo';
import { categoryIcon } from '../places';
import { onChange } from '../events';
import { resume } from '../tracker';
import { RememberSheet, TripSheet, VisitSheet } from '../components/Sheets';
import { Body, Button, Card, H1, H2, Stat, Sub, useTheme } from '../ui';

const isSameDay = (a: Date, b: Date) => a.toDateString() === b.toDateString();

export function Today() {
  const t = useTheme();
  const [day, setDay] = useState(() => new Date());
  const [sum, setSum] = useState<DaySummary | null>(null);
  const [steps, setSteps] = useState<StepResult | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [openVisit, setOpenVisit] = useState<Visit | null>(null);
  const [openTrip, setOpenTrip] = useState<Trip | null>(null);
  const [remembering, setRemembering] = useState(false);
  const today = isSameDay(day, new Date());

  const load = useCallback(() => {
    const s = summarizeDay(day);
    setSum(s);
    stepsBetween(s.start, s.end, s.walkedM).then(setSteps);
  }, [day]);

  useEffect(() => {
    load();
    const off = onChange(load);
    const timer = today ? setInterval(load, 30000) : undefined; // keep "ongoing" durations ticking
    return () => { off(); if (timer) clearInterval(timer); };
  }, [load, today]);

  const shift = (n: number) => { const d = new Date(day); d.setDate(d.getDate() + n); if (d <= new Date()) setDay(d); };

  if (!sum) return null;
  const now = sum.timeline[sum.timeline.length - 1];
  const known = sum.homeMs + sum.officeMs + sum.otherMs + sum.travelMs;

  return (
    <>
      <ScrollView style={{ backgroundColor: t.bg }} contentContainerStyle={{ padding: 16, paddingTop: 60, paddingBottom: 100 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={async () => { setRefreshing(true); await resume(); load(); setRefreshing(false); }} />}>
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
          <Pressable hitSlop={16} onPress={() => shift(-1)}><H1>‹</H1></Pressable>
          <View style={{ alignItems: 'center' }}>
            <H1>{today ? 'Today' : day.toLocaleDateString([], { weekday: 'long' })}</H1>
            <Sub>{day.toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' })}</Sub>
          </View>
          <Pressable hitSlop={16} onPress={() => shift(1)} disabled={today}><H1>{today ? ' ' : '›'}</H1></Pressable>
        </View>

        {today && now?.ongoing && (
          <Card style={{ marginTop: 16, borderColor: t.accent, borderWidth: 1.5 }}>
            <Sub>RIGHT NOW</Sub>
            <Body style={{ fontWeight: '700', fontSize: 18 }}>
              {now.type === 'visit'
                ? `${categoryIcon(now.visit.category)} At ${now.visit.name ?? now.visit.address ?? 'a place'} since ${formatTime(now.visit.start_ts)}`
                : `${MODE_LABEL[now.trip.mode ?? ''] ?? '🧭'} On the move since ${formatTime(now.trip.start_ts)}`}
            </Body>
          </Card>
        )}

        {today && <Button title="📌 Remember this place" kind="secondary" onPress={() => setRemembering(true)} style={{ marginTop: 12 }} />}

        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 16, marginBottom: 12 }}>
          <Stat label="Steps" value={steps ? steps.steps.toLocaleString() : '…'} color={t.home} hint={steps?.estimated ? 'estimated from walking' : undefined} />
          <Stat label="Distance travelled" value={formatDistance(sum.distanceM)} color={t.accent} />
          <Stat label="Time travelling" value={formatDuration(sum.travelMs)} color={t.travel} />
          <Stat label="Places visited" value={String(sum.placeTotals.length)} color={t.other} />
        </View>

        {(sum.commute.toOffice != null || sum.commute.toHome != null) && (
          <Card>
            <H2>🚗 Commute</H2>
            {sum.commute.toOffice != null && <Body>Home → Office: <Body style={{ fontWeight: '700' }}>{formatDuration(sum.commute.toOffice)}</Body></Body>}
            {sum.commute.toHome != null && <Body>Office → Home: <Body style={{ fontWeight: '700' }}>{formatDuration(sum.commute.toHome)}</Body></Body>}
          </Card>
        )}

        {known > 0 && (
          <Card>
            <H2>Where your time went</H2>
            <View style={{ flexDirection: 'row', height: 14, borderRadius: 7, overflow: 'hidden', marginBottom: 10 }}>
              {[[sum.homeMs, t.home], [sum.officeMs, t.office], [sum.otherMs, t.other], [sum.travelMs, t.travel]].map(([ms, c], i) =>
                (ms as number) > 0 ? <View key={i} style={{ flex: ms as number, backgroundColor: c as string }} /> : null)}
            </View>
            <Legend color={t.home} label="Home" ms={sum.homeMs} />
            <Legend color={t.office} label="Office" ms={sum.officeMs} />
            <Legend color={t.other} label="Other places" ms={sum.otherMs} />
            <Legend color={t.travel} label="Travelling" ms={sum.travelMs} />
            {Object.entries(sum.modeTotals).map(([m, v]) => (
              <Sub key={m} style={{ marginLeft: 20 }}>{MODE_LABEL[m] ?? m}: {formatDuration(v.ms)} · {formatDistance(v.m)}</Sub>
            ))}
          </Card>
        )}

        <H2 style={{ marginTop: 8 }}>Timeline</H2>
        {sum.timeline.length === 0 && (
          <Card><Sub>{today ? 'Nothing yet — your first place appears after you’ve stayed somewhere for about 5 minutes.' : 'No data for this day.'}</Sub></Card>
        )}
        {sum.timeline.map((item) => <Row key={`${item.type}${item.type === 'visit' ? item.visit.id : item.trip.id}`} item={item}
          onPress={() => (item.type === 'visit' ? setOpenVisit(item.visit) : setOpenTrip(item.trip))} />)}
      </ScrollView>
      <VisitSheet visit={openVisit} onClose={() => setOpenVisit(null)} />
      <TripSheet trip={openTrip} onClose={() => setOpenTrip(null)} />
      <RememberSheet visible={remembering} onClose={() => setRemembering(false)} />
    </>
  );
}

function Legend({ color, label, ms }: { color: string; label: string; ms: number }) {
  if (ms <= 0) return null;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', marginVertical: 2 }}>
      <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: color, marginRight: 8 }} />
      <Body style={{ flex: 1 }}>{label}</Body><Body style={{ fontWeight: '700' }}>{formatDuration(ms)}</Body>
    </View>
  );
}

function Row({ item, onPress }: { item: TimelineItem; onPress: () => void }) {
  const t = useTheme();
  const time = `${formatTime(item.start)} – ${item.ongoing ? 'now' : formatTime(item.end)}`;
  if (item.type === 'visit') {
    const v = item.visit;
    return (
      <Pressable onPress={onPress}>
        <Card style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Body style={{ fontSize: 28, marginRight: 12 }}>{categoryIcon(v.category)}</Body>
          <View style={{ flex: 1 }}>
            <Body style={{ fontWeight: '700' }}>{v.name ?? v.address ?? (v.resolved ? 'Unknown place' : 'Finding place…')}</Body>
            {v.name && v.address ? <Sub numberOfLines={1}>{v.address}</Sub> : null}
            <Sub>{time}</Sub>
          </View>
          <Body style={{ fontWeight: '700' }}>{formatDuration(item.end - item.start)}</Body>
        </Card>
      </Pressable>
    );
  }
  const tr = item.trip;
  return (
    <Pressable onPress={onPress}>
      <View style={{ flexDirection: 'row', alignItems: 'center', marginLeft: 22, marginBottom: 12, paddingLeft: 18,
        borderLeftWidth: 3, borderColor: t.travel, borderStyle: 'dashed', paddingVertical: 6 }}>
        <View style={{ flex: 1 }}>
          <Body>{MODE_LABEL[tr.mode ?? ''] ?? '🧭 Travelling'} · {formatDuration(item.end - item.start)}</Body>
          <Sub>{time}{tr.distance_m ? ` · ${formatDistance(tr.distance_m)}` : ''}  ›  view route</Sub>
        </View>
      </View>
    </Pressable>
  );
}
