import React, { useEffect, useState } from 'react';
import { Alert, Linking, Platform, ScrollView, Share, Switch, View } from 'react-native';
import * as Location from 'expo-location';
import { db, deleteAllData, getKV, setKV } from '../db';
import { isTracking, startTracking, stopTracking, TrackingMode } from '../tracker';
import { emitChange } from '../events';
import { connectHealthConnect, healthConnectStatus, HealthConnectStatus, openHealthConnect } from '../steps';
import { phoneGuide, requestUnrestrictedBattery } from '../reliability';
import { usingGooglePlaces } from '../places';
import { Body, Button, Card, Chip, H1, H2, Sub, useTheme } from '../ui';

export function Settings() {
  const t = useTheme();
  const [tracking, setTracking] = useState(false);
  const [mode, setMode] = useState<TrackingMode>(getKV('settings.mode', 'precise'));
  const [notify, setNotify] = useState(getKV('settings.notify', true));
  const [bgOk, setBgOk] = useState<boolean | null>(null);
  const [hcStatus, setHcStatus] = useState<HealthConnectStatus | null>(null);
  const guide = phoneGuide();

  const refresh = async () => {
    setTracking(await isTracking());
    setBgOk((await Location.getBackgroundPermissionsAsync()).granted);
    setHcStatus(await healthConnectStatus());
  };
  useEffect(() => { refresh(); }, []);

  const toggle = async (on: boolean) => {
    try { on ? await startTracking(mode) : await stopTracking(); } catch (e: any) { Alert.alert('Error', String(e?.message ?? e)); }
    refresh();
  };

  const counts = db.getFirstSync<{ p: number; v: number; tr: number }>(
    'SELECT (SELECT count(*) FROM points) p, (SELECT count(*) FROM visits) v, (SELECT count(*) FROM trips) tr');

  const exportData = async () => {
    const data = {
      places: db.getAllSync('SELECT * FROM places'),
      visits: db.getAllSync('SELECT * FROM visits'),
      trips: db.getAllSync('SELECT * FROM trips'),
    };
    await Share.share({ message: JSON.stringify(data), title: 'Day Tracker export' });
  };

  return (
    <ScrollView style={{ backgroundColor: t.bg }} contentContainerStyle={{ padding: 16, paddingTop: 60, paddingBottom: 100 }}>
      <H1>Settings</H1>

      <Card>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <View style={{ flex: 1 }}>
            <H2 style={{ marginBottom: 2 }}>Tracking</H2>
            <Sub>{tracking ? '🟢 Recording your day' : '⚪ Paused'}</Sub>
          </View>
          <Switch value={tracking} onValueChange={toggle} />
        </View>
        {bgOk === false && (
          <>
            <Sub style={{ color: t.danger, marginTop: 10 }}>Background location is not set to “{Platform.OS === 'android' ? 'Allow all the time' : 'Always'}”. Tracking will stop when the app is closed.</Sub>
            <Button title="Fix in Settings" kind="secondary" onPress={() => Linking.openSettings()} />
          </>
        )}
      </Card>

      <Card>
        <H2>Accuracy</H2>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
          <Chip label="🎯 Precise" active={mode === 'precise'} onPress={() => { setMode('precise'); if (tracking) startTracking('precise'); else setKV('settings.mode', 'precise'); }} />
          <Chip label="🔋 Battery saver" active={mode === 'balanced'} onPress={() => { setMode('balanced'); if (tracking) startTracking('balanced'); else setKV('settings.mode', 'balanced'); }} />
        </View>
        <Sub>Precise: detailed routes (GPS every ~15 m). Battery saver: fewer points, still records places and trips.</Sub>
      </Card>

      <Card>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <View style={{ flex: 1 }}>
            <H2 style={{ marginBottom: 2 }}>Arrival notifications</H2>
            <Sub>“Arrived at Office · 🚗 38 min”</Sub>
          </View>
          <Switch value={notify} onValueChange={(v) => { setNotify(v); setKV('settings.notify', v); }} />
        </View>
      </Card>

      <Card>
        <H2>Keep tracking reliable</H2>
        {Platform.OS === 'android' ? (
          <>
            <Sub>Phones pause background apps to save battery, which leaves gaps in your day. Do these once:</Sub>
            <Button title="1. Allow running in background" onPress={requestUnrestrictedBattery} />
            <Sub style={{ marginTop: 12, fontWeight: '700' }}>2. Extra steps for your phone ({guide.brand === 'other' ? 'Android' : guide.brand}):</Sub>
            {guide.steps.map((x, i) => <Sub key={i}>• {x}</Sub>)}
            <Button title="Open app settings" kind="secondary" onPress={() => Linking.openSettings()} />
            <Button title="Step-by-step guide with pictures" kind="secondary" onPress={() => Linking.openURL(guide.link)} />
          </>
        ) : (
          <>
            <Sub>• Keep Location set to “Always” with Precise Location on.</Sub>
            <Sub>• Don’t swipe Day Tracker away in the app switcher. iPhone fully stops apps you swipe away; it comes back when you arrive at or leave a saved place, or when you open it.</Sub>
            <Sub>• Low Power Mode reduces how often your location is recorded.</Sub>
          </>
        )}
        <Sub style={{ marginTop: 8 }}>Also running: a watchdog that restarts tracking if it stops, and arrival/departure alerts for your saved places that wake the app.</Sub>
      </Card>

      {Platform.OS === 'android' && (
        <Card>
          <H2>👣 Steps (Health Connect)</H2>
          <Sub>{{
            connected: '🟢 Connected: exact steps from your phone, watch, Google Fit or Samsung Health.',
            'not-connected': '⚪ Not connected: steps are estimated from walking distance.',
            'not-installed': '⚠️ Health Connect isn’t on this phone. Install it from the Play Store (built in on Android 14+).',
            'needs-update': '⚠️ Health Connect needs an update in the Play Store.',
            'not-android': '',
          }[hcStatus ?? 'not-connected']}</Sub>
          {hcStatus === 'not-installed' || hcStatus === 'needs-update' ? (
            <Button title="Get Health Connect" kind="secondary"
              onPress={() => Linking.openURL('market://details?id=com.google.android.apps.healthdata').catch(() =>
                Linking.openURL('https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata'))} />
          ) : hcStatus === 'connected' ? (
            <Button title="Health Connect settings" kind="secondary" onPress={openHealthConnect} />
          ) : (
            <Button title="Connect Health Connect" onPress={async () => { setHcStatus(await connectHealthConnect()); emitChange(); }} />
          )}
          <Sub style={{ marginTop: 6 }}>No steps showing? In Health Connect, turn on step counting for this phone, or let Google Fit / Samsung Health / your watch app write steps to it.</Sub>
        </Card>
      )}

      <Card>
        <H2>Place names</H2>
        <Sub>{usingGooglePlaces ? '🟢 Google Places + OpenStreetMap' : '🟢 OpenStreetMap (free). Add a Google Places key for better coverage – see README.'}</Sub>
        <Sub>Names you pick for a visit are remembered and reused automatically.</Sub>
      </Card>

      <Card>
        <H2>Your data</H2>
        <Body>{counts?.v ?? 0} visits · {counts?.tr ?? 0} trips · {counts?.p ?? 0} GPS points</Body>
        <Sub>Stored only on this phone.</Sub>
        <Button title="Export (JSON)" kind="secondary" onPress={exportData} />
        <Button title="Delete all history" kind="danger" onPress={() => Alert.alert('Delete all history?',
          'Visits, trips and routes are erased. Your saved places are kept.', [
            { text: 'Cancel' },
            { text: 'Delete', style: 'destructive', onPress: async () => {
              const was = await isTracking();
              if (was) await stopTracking();
              deleteAllData();
              if (was) await startTracking(mode);
              emitChange(); refresh();
            } }])} />
      </Card>
    </ScrollView>
  );
}
