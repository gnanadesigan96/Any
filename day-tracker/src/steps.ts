import { Platform } from 'react-native';
import { Pedometer } from 'expo-sensors';

export interface StepResult { steps: number; estimated: boolean }

/**
 * iPhone: real step count from the motion chip for any time range.
 * Android: the system API only gives live steps while the app is open, so we
 * estimate from the distance you walked (≈ 0.75 m per step).
 */
export async function stepsBetween(start: number, end: number, walkedMetres: number): Promise<StepResult> {
  if (Platform.OS === 'ios') {
    try {
      if (await Pedometer.isAvailableAsync()) {
        const r = await Pedometer.getStepCountAsync(new Date(start), new Date(end));
        return { steps: r.steps, estimated: false };
      }
    } catch {}
  }
  return { steps: Math.round(walkedMetres / 0.75), estimated: true };
}
