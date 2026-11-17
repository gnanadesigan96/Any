import React, { useCallback, useEffect, useState } from 'react';
import { View } from 'react-native';
import { dayBounds, Point, pointsBetween, Visit, visitsOverlapping } from '../db';
import { onChange } from '../events';
import { RouteMap } from '../components/RouteMap';
import { H1, Sub, useTheme } from '../ui';

/** Everything you did today on one map: the full route plus every stop. */
export function MapScreen() {
  const t = useTheme();
  const [points, setPoints] = useState<Point[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);

  const load = useCallback(() => {
    const [from, to] = dayBounds(new Date());
    setPoints(pointsBetween(from, to));
    setVisits(visitsOverlapping(from, to));
  }, []);
  useEffect(() => { load(); return onChange(load); }, [load]);

  return (
    <View style={{ flex: 1, backgroundColor: t.bg, padding: 16, paddingTop: 60, paddingBottom: 90 }}>
      <H1>Today’s map</H1>
      <Sub style={{ marginBottom: 12 }}>{visits.length} stops · {points.length} GPS points. Updates live as you move.</Sub>
      <RouteMap points={points} visits={visits} live style={{ flex: 1 }} />
    </View>
  );
}
