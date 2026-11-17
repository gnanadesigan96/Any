import type { ExpoConfig } from 'expo/config';

// Google Maps key is only needed for the map on Android (iOS uses Apple Maps).
// Put it in a local .env file as GOOGLE_MAPS_API_KEY=... — never commit it.
const googleMapsKey = process.env.GOOGLE_MAPS_API_KEY ?? '';

const config: ExpoConfig = {
  name: 'Day Tracker',
  slug: 'day-tracker',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'automatic',
  ios: {
    supportsTablet: false,
    bundleIdentifier: 'com.daytracker.app',
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
    ['react-native-maps', { androidGoogleMapsApiKey: googleMapsKey }],
  ],
};

export default config;
