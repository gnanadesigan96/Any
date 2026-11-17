import { Linking, Platform } from 'react-native';
import * as Device from 'expo-device';
import * as IntentLauncher from 'expo-intent-launcher';
import Constants from 'expo-constants';

const PACKAGE = Constants.expoConfig?.android?.package ?? 'com.daytracker.app';

/** Shows Android's own "Let app always run in background?" dialog. */
export async function requestUnrestrictedBattery() {
  if (Platform.OS !== 'android') return;
  try {
    await IntentLauncher.startActivityAsync(IntentLauncher.ActivityAction.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, { data: `package:${PACKAGE}` });
  } catch {
    try { await IntentLauncher.startActivityAsync(IntentLauncher.ActivityAction.IGNORE_BATTERY_OPTIMIZATION_SETTINGS); }
    catch { Linking.openSettings(); }
  }
}

export function openAppSettings() { Linking.openSettings(); }

/** Brand-specific steps: these phones have their own extra battery killers on top of Android's. */
export function phoneGuide(): { brand: string; steps: string[]; link: string } {
  const raw = (Device.manufacturer ?? Device.brand ?? '').toLowerCase();
  const brand = raw.includes('samsung') ? 'samsung' : raw.includes('xiaomi') || raw.includes('redmi') || raw.includes('poco') ? 'xiaomi'
    : raw.includes('oneplus') ? 'oneplus' : raw.includes('vivo') || raw.includes('iqoo') ? 'vivo'
    : raw.includes('oppo') || raw.includes('realme') ? 'oppo' : raw.includes('huawei') || raw.includes('honor') ? 'huawei'
    : raw.includes('motorola') ? 'motorola' : raw.includes('google') ? 'google' : 'other';
  const common = 'In Day Tracker’s app info → Battery, choose “Unrestricted”.';
  const steps: Record<string, string[]> = {
    samsung: [common, 'Settings → Battery → Background usage limits → make sure Day Tracker is NOT in “Sleeping” or “Deep sleeping” apps.',
      'Add Day Tracker to “Never sleeping apps”.'],
    xiaomi: ['App info → Battery saver → “No restrictions”.', 'App info → turn on “Autostart”.',
      'Open recent apps, long-press Day Tracker and tap the lock icon so it is not cleared.'],
    oneplus: [common, 'Settings → Battery → Battery optimisation → Day Tracker → “Don’t optimise”.', 'Lock the app in recent apps.'],
    vivo: ['Settings → Battery → Background power consumption → allow Day Tracker.', 'i Manager → App manager → Autostart → allow Day Tracker.',
      'Lock the app in recent apps.'],
    oppo: ['App info → Battery usage → allow background activity and auto launch.', 'Lock the app in recent apps.'],
    huawei: ['Settings → Battery → App launch → Day Tracker → Manage manually, turn all three switches on.'],
    motorola: [common],
    google: [common],
    other: [common, 'If your phone has its own “battery saver” or “auto-start” manager, allow Day Tracker there too.'],
  };
  return { brand, steps: steps[brand], link: `https://dontkillmyapp.com/${brand === 'other' ? '' : brand}` };
}
