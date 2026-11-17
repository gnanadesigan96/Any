import React, { useState } from 'react';
import { Alert, Linking, Platform, ScrollView, View } from 'react-native';
import * as Location from 'expo-location';
import * as Notifications from 'expo-notifications';
import { Pedometer } from 'expo-sensors';
import { setKV } from '../db';
import { startTracking } from '../tracker';
import { connectHealthConnect } from '../steps';
import { phoneGuide, requestUnrestrictedBattery } from '../reliability';
import { PlaceEditor } from '../components/PlaceEditor';
import { Body, Button, Card, H1, H2, Sub, useTheme } from '../ui';

type Step = 'welcome' | 'location' | 'background' | 'extras' | 'home' | 'office' | 'done';
const ORDER: Step[] = ['welcome', 'location', 'background', 'extras', 'home', 'office', 'done'];

export function Onboarding({ onFinish }: { onFinish: () => void }) {
  const t = useTheme();
  const [step, setStep] = useState<Step>('welcome');
  const [busy, setBusy] = useState(false);
  const next = () => setStep(ORDER[ORDER.indexOf(step) + 1]);

  async function askForeground() {
    setBusy(true);
    try {
      if (!(await Location.hasServicesEnabledAsync())) {
        Alert.alert('Turn on Location', 'Location services are off. Turn them on in your phone settings, then come back.');
        return;
      }
      const r = await Location.requestForegroundPermissionsAsync();
      if (r.granted) next();
      else Alert.alert('Location needed', 'Day Tracker can’t work without location. You can allow it in Settings.',
        [{ text: 'Open Settings', onPress: () => Linking.openSettings() }, { text: 'Cancel' }]);
    } finally { setBusy(false); }
  }

  async function askBackground() {
    setBusy(true);
    try {
      const r = await Location.requestBackgroundPermissionsAsync();
      if (r.granted) next();
      else Alert.alert(
        'Choose “Allow all the time”',
        Platform.OS === 'android'
          ? 'Open Settings → Permissions → Location and pick “Allow all the time”. Without it, tracking stops when you close the app.'
          : 'Open Settings → Location and pick “Always”, with Precise Location on. Without it, tracking stops when you close the app.',
        [{ text: 'Open Settings', onPress: () => Linking.openSettings() }, { text: 'Continue anyway', onPress: next }]);
    } finally { setBusy(false); }
  }

  async function askExtras() {
    setBusy(true);
    try {
      await Notifications.requestPermissionsAsync().catch(() => null);
      await Pedometer.requestPermissionsAsync().catch(() => null);
      if (Platform.OS === 'android') {
        await Location.requestMotionActivityPermissionsAsync().catch(() => null);
        const hc = await connectHealthConnect().catch(() => null);
        if (hc === 'not-installed' || hc === 'needs-update') {
          Alert.alert('Health Connect', 'For exact step counts install or update Health Connect from the Play Store. Until then steps are estimated. You can connect it later in Settings.');
        }
      }
      next();
    } finally { setBusy(false); }
  }

  async function finish() {
    setBusy(true);
    try {
      await startTracking('precise');
      setKV('settings.onboarded', true);
      onFinish();
    } catch (e: any) {
      Alert.alert('Could not start tracking', String(e?.message ?? e));
    } finally { setBusy(false); }
  }

  const progress = (ORDER.indexOf(step) / (ORDER.length - 1)) * 100;

  return (
    <ScrollView contentContainerStyle={{ padding: 20, paddingTop: 64, paddingBottom: 48 }} keyboardShouldPersistTaps="handled"
      style={{ backgroundColor: t.bg }}>
      <View style={{ height: 4, backgroundColor: t.border, borderRadius: 2, marginBottom: 24 }}>
        <View style={{ height: 4, width: `${progress}%`, backgroundColor: t.accent, borderRadius: 2 }} />
      </View>

      {step === 'welcome' && (
        <>
          <H1>Your day, automatically</H1>
          <Body>Day Tracker builds a timeline of your day on its own:</Body>
          <Card style={{ marginTop: 16 }}>
            <Body>🏠  When you leave home and arrive at the office</Body>
            <Body>🗺️  The exact route and how long the commute took</Body>
            <Body>🍽️  Restaurants, shops and places you stop at</Body>
            <Body>👣  Steps, distance and time spent travelling</Body>
          </Card>
          <Sub>🔒 Everything is stored only on this phone. Place names are looked up on OpenStreetMap using the coordinates of each stop, without any account or personal info.</Sub>
          <Button title="Get started" onPress={next} />
        </>
      )}

      {step === 'location' && (
        <>
          <H1>Allow location</H1>
          <Body>First, allow Day Tracker to use your location. Choose <Body style={{ fontWeight: '700' }}>Precise</Body> location if asked — it’s needed to tell apart places next to each other.</Body>
          <Button title="Allow location" busy={busy} onPress={askForeground} />
        </>
      )}

      {step === 'background' && (
        <>
          <H1>Track all day</H1>
          <Body>To record your commute while the phone is in your pocket, Day Tracker needs location access
            <Body style={{ fontWeight: '700' }}>{Platform.OS === 'android' ? ' “Allow all the time”' : ' “Always”'}</Body>.</Body>
          <Card style={{ marginTop: 16 }}>
            <Sub>{Platform.OS === 'android'
              ? 'On the next screen tap “Allow all the time”. You will see a small notification while tracking is on — that is what keeps it running reliably.'
              : 'On the next prompt tap “Change to Always Allow”. A blue location indicator may appear in the status bar while tracking.'}</Sub>
          </Card>
          <Button title="Allow all the time" busy={busy} onPress={askBackground} />
        </>
      )}

      {step === 'extras' && (
        <>
          <H1>Steps & alerts</H1>
          <Body>Allow {Platform.OS === 'android' ? 'Health Connect (step count)' : 'Motion & Fitness'} access to count steps, and notifications so you get a note like
            “Arrived at Office · 38 min commute”.</Body>
          {Platform.OS === 'android' && (
            <Card style={{ marginTop: 16 }}>
              <H2>Important on Android</H2>
              <Sub>Phones stop background apps to save battery. Tap below and choose “Allow” so tracking never pauses.</Sub>
              <Button title="Allow running in background" kind="secondary" onPress={requestUnrestrictedBattery} />
              {phoneGuide().brand !== 'google' && phoneGuide().brand !== 'other' && (
                <Sub style={{ marginTop: 8 }}>Your {phoneGuide().brand} phone needs one more step — it’s shown in Settings → Keep tracking reliable.</Sub>
              )}
            </Card>
          )}
          <Button title="Continue" busy={busy} onPress={askExtras} />
        </>
      )}

      {step === 'home' && (
        <>
          <H1>Where is home?</H1>
          <Sub style={{ marginBottom: 12 }}>We’ll label your time here as “Home”. If you’re home now, just tap Save.</Sub>
          <PlaceEditor kind="home" onSaved={next} />
        </>
      )}

      {step === 'office' && (
        <>
          <H1>Where do you work?</H1>
          <Sub style={{ marginBottom: 12 }}>Used to measure your commute (Home → Office and back). Search the address or drop the pin.</Sub>
          <PlaceEditor kind="office" onSaved={next} onSkip={next} />
        </>
      )}

      {step === 'done' && (
        <>
          <H1>All set 🎉</H1>
          <Body>Go about your day. Day Tracker will notice when you leave, the route you take, and where you stop.</Body>
          <Card style={{ marginTop: 16 }}>
            <Sub>A stop counts as a visit after about 5 minutes in one place. You can rename any place or fix the travel mode later by tapping it in the timeline.</Sub>
          </Card>
          <Button title="Start tracking" busy={busy} onPress={finish} />
        </>
      )}
    </ScrollView>
  );
}
