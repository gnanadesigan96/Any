import type { ExpoConfig } from 'expo/config';

const config: ExpoConfig = {
  name: 'Day Tracker',
  slug: 'day-tracker',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'automatic',
  ios: {
    supportsTablet: false,
    // Must be unique on the App Store: set IOS_BUNDLE_ID (e.g. com.yourname.daytracker) when publishing.
    bundleIdentifier: process.env.IOS_BUNDLE_ID || 'com.daytracker.app',
    buildNumber: process.env.IOS_BUILD_NUMBER || '1',
    config: { usesNonExemptEncryption: false },
    infoPlist: {
      UIBackgroundModes: ['location', 'fetch', 'processing'],
    },
  },
  android: {
    package: 'com.daytracker.app',
    adaptiveIcon: {
      backgroundColor: '#E6F4FE',
      foregroundImage: './assets/android-icon-foreground.png',
      backgroundImage: './assets/android-icon-background.png',
      monochromeImage: './assets/android-icon-monochrome.png',
    },
    permissions: [
      'ACCESS_COARSE_LOCATION',
      'ACCESS_FINE_LOCATION',
      'ACCESS_BACKGROUND_LOCATION',
      'FOREGROUND_SERVICE',
      'FOREGROUND_SERVICE_LOCATION',
      'ACTIVITY_RECOGNITION',
      'POST_NOTIFICATIONS',
      'RECEIVE_BOOT_COMPLETED',
      'REQUEST_IGNORE_BATTERY_OPTIMIZATIONS',
      'android.permission.health.READ_STEPS',
      'android.permission.health.READ_HEALTH_DATA_IN_BACKGROUND',
    ],
    predictiveBackGestureEnabled: false,
  },
  plugins: [
    'expo-sqlite',
    [
      'expo-location',
      {
        locationAlwaysAndWhenInUsePermission:
          'Day Tracker records the places you visit and the routes you travel, even when the app is closed, so it can build your daily timeline. Your data stays on this phone.',
        locationWhenInUsePermission:
          'Day Tracker uses your location to set your Home and Office and to show where you are.',
        isIosBackgroundLocationEnabled: true,
        isAndroidBackgroundLocationEnabled: true,
        isAndroidForegroundServiceEnabled: true,
      },
    ],
    [
      'expo-sensors',
      {
        motionPermission: 'Day Tracker counts your steps to show how active you were each day.',
      },
    ],
    'expo-notifications',
    'expo-background-task',
    // Real step counts on Android come from Health Connect (needs Android 8+).
    'react-native-health-connect',
    ['expo-build-properties', { android: { minSdkVersion: 26 } }],
    // Our own map: MapLibre + OpenStreetMap data (no Google, no key).
    '@maplibre/maplibre-react-native',
  ],
};

export default config;
