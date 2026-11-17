import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, TextInputProps, useColorScheme, View, ViewStyle } from 'react-native';

export interface Theme {
  bg: string; card: string; text: string; sub: string; border: string;
  accent: string; accentText: string; home: string; office: string; travel: string; other: string; danger: string;
}
const light: Theme = {
  bg: '#F4F6FA', card: '#FFFFFF', text: '#0F172A', sub: '#64748B', border: '#E2E8F0',
  accent: '#2563EB', accentText: '#FFFFFF', home: '#16A34A', office: '#7C3AED', travel: '#F59E0B', other: '#0EA5E9', danger: '#DC2626',
};
const dark: Theme = {
  bg: '#0B1120', card: '#151E2F', text: '#F1F5F9', sub: '#94A3B8', border: '#26324A',
  accent: '#3B82F6', accentText: '#FFFFFF', home: '#22C55E', office: '#A78BFA', travel: '#FBBF24', other: '#38BDF8', danger: '#F87171',
};
export function useTheme(): Theme {
  return useColorScheme() === 'dark' ? dark : light;
}

export function Card({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  const t = useTheme();
  return <View style={[styles.card, { backgroundColor: t.card, borderColor: t.border }, style]}>{children}</View>;
}

export function H1({ children }: { children: React.ReactNode }) {
  const t = useTheme();
  return <Text style={[styles.h1, { color: t.text }]}>{children}</Text>;
}
export function H2({ children, style }: { children: React.ReactNode; style?: object }) {
  const t = useTheme();
  return <Text style={[styles.h2, { color: t.text }, style]}>{children}</Text>;
}
export function Sub({ children, style, numberOfLines }: { children: React.ReactNode; style?: object; numberOfLines?: number }) {
  const t = useTheme();
  return <Text numberOfLines={numberOfLines} style={[styles.sub, { color: t.sub }, style]}>{children}</Text>;
}
export function Body({ children, style }: { children: React.ReactNode; style?: object }) {
  const t = useTheme();
  return <Text style={[styles.body, { color: t.text }, style]}>{children}</Text>;
}

export function Button({ title, onPress, kind = 'primary', busy, disabled, style }: {
  title: string; onPress: () => void; kind?: 'primary' | 'secondary' | 'danger'; busy?: boolean; disabled?: boolean; style?: ViewStyle;
}) {
  const t = useTheme();
  const bg = kind === 'primary' ? t.accent : kind === 'danger' ? t.danger : 'transparent';
  const fg = kind === 'secondary' ? t.accent : t.accentText;
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled || busy}
      style={({ pressed }) => [styles.btn, { backgroundColor: bg, borderColor: kind === 'secondary' ? t.accent : bg,
        opacity: disabled ? 0.45 : pressed ? 0.8 : 1 }, style]}>
      {busy ? <ActivityIndicator color={fg} /> : <Text style={[styles.btnText, { color: fg }]}>{title}</Text>}
    </Pressable>
  );
}

export function Chip({ label, active, onPress }: { label: string; active?: boolean; onPress: () => void }) {
  const t = useTheme();
  return (
    <Pressable onPress={onPress} style={[styles.chip, { borderColor: active ? t.accent : t.border, backgroundColor: active ? t.accent : t.card }]}>
      <Text style={{ color: active ? t.accentText : t.text, fontWeight: '600' }}>{label}</Text>
    </Pressable>
  );
}

export function Input(props: TextInputProps) {
  const t = useTheme();
  return <TextInput placeholderTextColor={t.sub} {...props}
    style={[styles.input, { color: t.text, borderColor: t.border, backgroundColor: t.card }, props.style]} />;
}

export function Stat({ label, value, color, hint }: { label: string; value: string; color?: string; hint?: string }) {
  const t = useTheme();
  return (
    <View style={[styles.stat, { backgroundColor: t.card, borderColor: t.border }]}>
      <View style={[styles.statBar, { backgroundColor: color ?? t.accent }]} />
      <Text style={[styles.statValue, { color: t.text }]} numberOfLines={1}>{value}</Text>
      <Text style={[styles.statLabel, { color: t.sub }]} numberOfLines={1}>{label}</Text>
      {hint ? <Text style={[styles.statHint, { color: t.sub }]}>{hint}</Text> : null}
    </View>
  );
}

export const styles = StyleSheet.create({
  card: { borderRadius: 16, borderWidth: StyleSheet.hairlineWidth, padding: 16, marginBottom: 12 },
  h1: { fontSize: 28, fontWeight: '800', marginBottom: 6 },
  h2: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  sub: { fontSize: 14, lineHeight: 20 },
  body: { fontSize: 16, lineHeight: 22 },
  btn: { borderRadius: 12, borderWidth: 1.5, paddingVertical: 14, paddingHorizontal: 18, alignItems: 'center', marginTop: 10, minHeight: 50, justifyContent: 'center' },
  btnText: { fontSize: 16, fontWeight: '700' },
  chip: { borderRadius: 999, borderWidth: 1, paddingVertical: 8, paddingHorizontal: 14, marginRight: 8, marginBottom: 8 },
  input: { borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, fontSize: 16, marginTop: 8 },
  stat: { flexBasis: '47%', flexGrow: 1, borderRadius: 14, borderWidth: StyleSheet.hairlineWidth, padding: 14, overflow: 'hidden' },
  statBar: { position: 'absolute', left: 0, top: 0, bottom: 0, width: 4 },
  statValue: { fontSize: 22, fontWeight: '800' },
  statLabel: { fontSize: 13, marginTop: 2 },
  statHint: { fontSize: 11, marginTop: 2 },
});
