import React from 'react';
import { ViewStyle } from 'react-native';
import { Point, Visit } from '../db';
import { categoryIcon } from '../places';
import { AppMap } from './AppMap';

/** A route (GPS points) plus place pins, zoomed to fit. */
export function RouteMap({ points, visits = [], style, live }: { points: Point[]; visits?: Visit[]; style?: ViewStyle; live?: boolean }) {
  return (
    <AppMap
      route={points}
      pins={visits.map((v) => ({ id: String(v.id), lat: v.lat, lon: v.lon, icon: categoryIcon(v.category), label: v.name ?? v.address ?? 'Visit' }))}
      live={live}
      style={style}
    />
  );
}
