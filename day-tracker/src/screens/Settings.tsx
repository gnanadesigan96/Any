import React, { useEffect, useState } from 'react';
import { Alert, Linking, Platform, ScrollView, Share, Switch, View } from 'react-native';
import * as Location from 'expo-location';
import { db, deleteAllData, getKV, setKV } from '../db';
import { isTracking, startTracking, stopTracking, TrackingMode } from '../tracker';
import { emitChange } from '../events';
import { Body, Button, Card, Chip, H1, H2, Sub, useTheme } from '../ui';

export function Settings() {
  const t = useTheme();
  const [tracking, setTracking] = useState(false);
  const [mode, setMode] = useState<TrackingMode>(getKV('settings.mode', 'precise'));
  const [notify, setNotify] = useState(getKV('settings.notify', true));
  const [bgOk, setBgOk] = useState<boolean | null>(null);

  const refresh = async () => {
    setTracking(await isTracking());
    setBgOk((await Location.getBackgroundPermissionsAsync()).granted);
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

      {Platform.OS === 'android' && (
        <Card>
          <H2>Keep tracking reliable</H2>
          <Sub>If days have gaps, set Day Tracker’s battery usage to “Unrestricted”.</Sub>
          <Button title="Battery settings" kind="secondary"
            onPress={() => Linking.sendIntent('android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS').catch(() => Linking.openSettings())} />
        </Card>
      )}

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
