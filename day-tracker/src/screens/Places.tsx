import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Modal, Pressable, ScrollView, View } from 'react-native';
import { deletePlace, listPlaces, Place, PlaceKind } from '../db';
import { categoryIcon } from '../places';
import { emitChange, onChange } from '../events';
import { PlaceEditor } from '../components/PlaceEditor';
import { Body, Button, Card, H1, Sub, useTheme } from '../ui';

export function Places() {
  const t = useTheme();
  const [places, setPlaces] = useState<Place[]>([]);
  const [editing, setEditing] = useState<{ kind: PlaceKind; place?: Place } | null>(null);
  const load = useCallback(() => setPlaces(listPlaces()), []);
  useEffect(() => { load(); return onChange(load); }, [load]);

  const has = (k: PlaceKind) => places.some((p) => p.kind === k);

  return (
    <>
      <ScrollView style={{ backgroundColor: t.bg }} contentContainerStyle={{ padding: 16, paddingTop: 60, paddingBottom: 100 }}>
        <H1>My places</H1>
        <Sub style={{ marginBottom: 16 }}>Saved places are always recognised by your name for them. Everything else is looked up automatically.</Sub>
        {places.map((p) => (
          <Pressable key={p.id} onPress={() => setEditing({ kind: p.kind, place: p })}>
            <Card style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Body style={{ fontSize: 28, marginRight: 12 }}>{categoryIcon(p.kind === 'other' ? 'other' : p.kind)}</Body>
              <View style={{ flex: 1 }}>
                <Body style={{ fontWeight: '700' }}>{p.name}</Body>
                <Sub numberOfLines={1}>{p.address ?? `${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`}</Sub>
                <Sub>within {p.radius} m</Sub>
              </View>
              <Pressable hitSlop={12} onPress={() => Alert.alert(`Delete ${p.name}?`, 'Past visits keep their times but lose this label.', [
                { text: 'Cancel' }, { text: 'Delete', style: 'destructive', onPress: () => { deletePlace(p.id); emitChange(); } }])}>
                <Body style={{ color: t.danger }}>Delete</Body>
              </Pressable>
            </Card>
          </Pressable>
        ))}
        {!has('home') && <Button title="🏠 Set Home" onPress={() => setEditing({ kind: 'home' })} />}
        {!has('office') && <Button title="🏢 Set Office" onPress={() => setEditing({ kind: 'office' })} />}
        <Button title="📌 Remember a place (address, street, gym…)" kind="secondary" onPress={() => setEditing({ kind: 'other' })} />
      </ScrollView>

      <Modal visible={!!editing} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setEditing(null)}>
        <ScrollView style={{ backgroundColor: t.bg }} contentContainerStyle={{ padding: 20, paddingBottom: 48 }} keyboardShouldPersistTaps="handled">
          <Pressable onPress={() => setEditing(null)} style={{ alignSelf: 'flex-end' }}><Body style={{ color: t.accent, fontWeight: '700' }}>Cancel</Body></Pressable>
          <H1>{editing?.place ? `Edit ${editing.place.name}` : editing?.kind === 'home' ? 'Set Home' : editing?.kind === 'office' ? 'Set Office' : 'New place'}</H1>
          {editing && (
            <PlaceEditor kind={editing.kind} initial={editing.place} allowKindChange={!editing.place && editing.kind === 'other'} onSaved={() => { setEditing(null); emitChange(); }} />
          )}
        </ScrollView>
      </Modal>
    </>
  );
}
