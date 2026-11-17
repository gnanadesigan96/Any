import { Platform } from 'react-native';
import { Pedometer } from 'expo-sensors';
import { getKV, setKV } from './db';

export type StepSource = 'iphone' | 'health-connect' | 'estimate';
export interface StepResult { steps: number; source: StepSource; hint?: string }

// Health Connect is Android-only; load it lazily so iOS never touches the native module.
type HC = typeof import('react-native-health-connect');
function hc(): HC | null {
  if (Platform.OS !== 'android') return null;
  try { return require('react-native-health-connect') as HC; } catch { return null; }
}

export type HealthConnectStatus = 'not-android' | 'not-installed' | 'needs-update' | 'not-connected' | 'connected';

let initialised = false;
async function init(h: HC): Promise<boolean> {
  if (initialised) return true;
  initialised = await h.initialize().catch(() => false);
  return initialised;
}

export async function healthConnectStatus(): Promise<HealthConnectStatus> {
  const h = hc();
  if (!h) return 'not-android';
  const sdk = await h.getSdkStatus().catch(() => h.SdkAvailabilityStatus.SDK_UNAVAILABLE);
  if (sdk === h.SdkAvailabilityStatus.SDK_UNAVAILABLE) return 'not-installed';
  if (sdk === h.SdkAvailabilityStatus.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED) return 'needs-update';
  if (!(await init(h))) return 'not-installed';
  const granted = await h.getGrantedPermissions().catch(() => []);
  return granted.some((p) => p.recordType === 'Steps') ? 'connected' : 'not-connected';
}

/** Ask for permission to read steps (and to read them while the app is in the background). */
export async function connectHealthConnect(): Promise<HealthConnectStatus> {
  const h = hc();
  if (!h) return 'not-android';
  const status = await healthConnectStatus();
  if (status === 'not-installed' || status === 'needs-update') return status;
  await h.requestPermission([
    { accessType: 'read', recordType: 'Steps' },
    { accessType: 'read', recordType: 'BackgroundAccessPermission' },
  ]).catch(() => []);
  const now = await healthConnectStatus();
  setKV('settings.healthConnect', now === 'connected');
  return now;
}

export function openHealthConnect() {
  hc()?.openHealthConnectSettings();
}

async function healthConnectSteps(start: number, end: number): Promise<number | null> {
  const h = hc();
  if (!h || !getKV('settings.healthConnect', false)) return null;
  try {
    if (!(await init(h))) return null;
    const r = await h.aggregateRecord({
      recordType: 'Steps',
      timeRangeFilter: { operator: 'between', startTime: new Date(start).toISOString(), endTime: new Date(end).toISOString() },
    });
    return r.COUNT_TOTAL;
  } catch {
    return null;
  }
}

/** Raw step count for a time range from the best real source, or null if none is available. */
export async function realSteps(start: number, end: number): Promise<{ steps: number; source: StepSource } | null> {
  if (Platform.OS === 'ios') {
    try {
      if (await Pedometer.isAvailableAsync()) {
        const r = await Pedometer.getStepCountAsync(new Date(start), new Date(end));
        return { steps: r.steps, source: 'iphone' };
      }
    } catch {}
    return null;
  }
  const n = await healthConnectSteps(start, end);
  return n == null ? null : { steps: n, source: 'health-connect' };
}

/**
 * Steps for a day.
 * iPhone: the motion chip. Android: Health Connect (fed by the phone, Google Fit, Samsung Health,
 * Fitbit, a watch…). Falls back to an estimate from walking distance (≈ 0.75 m per step).
 */
export async function stepsBetween(start: number, end: number, walkedMetres: number): Promise<StepResult> {
  const estimate = Math.round(walkedMetres / 0.75);
  const real = await realSteps(start, end);
  if (real) {
    // Health Connect connected but empty while you clearly walked: nothing is writing steps into it.
    if (real.source === 'health-connect' && real.steps === 0 && walkedMetres > 400) {
      return { steps: estimate, source: 'estimate',
        hint: 'Health Connect has no steps yet. Turn on step counting in Health Connect, Google Fit or Samsung Health.' };
    }
    return real;
  }
  return {
    steps: estimate, source: 'estimate',
    hint: Platform.OS === 'android' ? 'Connect Health Connect in Settings for exact steps.' : undefined,
  };
}
