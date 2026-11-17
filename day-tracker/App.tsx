import React, { useEffect, useState } from 'react';
import { AppState, Pressable, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as Notifications from 'expo-notifications';
import { getKV } from './src/db';
import { resume } from './src/tracker';
import { Onboarding } from './src/screens/Onboarding';
import { Today } from './src/screens/Today';
import { MapScreen } from './src/screens/MapScreen';
import { Places } from './src/screens/Places';
import { Settings } from './src/screens/Settings';
import { useTheme } from './src/ui';

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: false, shouldSetBadge: false }),
});

const TABS = [
  { key: 'today', label: 'Today', icon: '📅' },
  { key: 'map', label: 'Map', icon: '🗺️' },
  { key: 'places', label: 'Places', icon: '⭐' },
  { key: 'settings', label: 'Settings', icon: '⚙️' },
] as const;
type TabKey = (typeof TABS)[number]['key'];

export default function App() {
  const t = useTheme();
  const [onboarded, setOnboarded] = useState(() => getKV('settings.onboarded', false));
  const [tab, setTab] = useState<TabKey>('today');

  useEffect(() => {
    if (!onboarded) return;
    resume();
    const sub = AppState.addEventListener('change', (s) => { if (s === 'active') resume(); });
    return () => sub.remove();
  }, [onboarded]);

  if (!onboarded) return (<><StatusBar style="auto" /><Onboarding onFinish={() => setOnboarded(true)} /></>);

  return (
    <View style={{ flex: 1, backgroundColor: t.bg }}>
      <StatusBar style="auto" />
      <View style={{ flex: 1 }}>
        {tab === 'today' && <Today />}
        {tab === 'map' && <MapScreen />}
        {tab === 'places' && <Places />}
        {tab === 'settings' && <Settings />}
      </View>
      <View style={[s.bar, { backgroundColor: t.card, borderColor: t.border }]}>
        {TABS.map((x) => (
          <Pressable key={x.key} style={s.tab} onPress={() => setTab(x.key)} accessibilityRole="tab" accessibilityState={{ selected: tab === x.key }}>
            <Text style={{ fontSize: 22, opacity: tab === x.key ? 1 : 0.5 }}>{x.icon}</Text>
            <Text style={{ fontSize: 12, fontWeight: '600', color: tab === x.key ? t.accent : t.sub }}>{x.label}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  bar: { flexDirection: 'row', borderTopWidth: StyleSheet.hairlineWidth, paddingBottom: 24, paddingTop: 8 },
  tab: { flex: 1, alignItems: 'center', gap: 2 },
});
