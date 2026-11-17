# Day Tracker

A phone app (Android + iPhone) that records your day on its own: where you went, when you
arrived and left, the route you took, how long each journey took, the restaurants and shops
you stopped at, and your steps.

## What it does

- **Setup wizard**: asks for location ("Allow all the time"), motion/steps and notifications,
  then has you set **Home** and **Office** (current location, typed address, or drag the pin).
- **Automatic timeline**: a stop of about 5 minutes or more becomes a *visit*; the movement between
  stops becomes a *trip*, with times, distance, speed, the full GPS route and a guess at how you travelled
  (walk / cycle / vehicle …, one tap to correct).
- **Place recognition**: saved places (Home, Office, your own) first; otherwise the nearest
  restaurant / café / shop / hospital etc. from OpenStreetMap; otherwise the street address.
  Tap any visit to choose from nearby places or type a name.
- **📌 Remember this place**: save where you are now, a typed address, or a whole street/area
  (up to 500 m) as Home, Office or any name. Past visits there are re-labelled too.
- **Daily analysis**: steps, distance, time travelling, Home → Office and Office → Home commute,
  a time breakdown (home / office / other / travel), time per travel mode, and any past day.
- **Arrival notifications**: "Arrived at Office · 🚗 Vehicle · 38 min · 12.4 km".
- **Private**: everything is stored in SQLite on the phone. Export as JSON or delete it from Settings.

## Run it on your phone

Background location doesn't work in Expo Go, so you need a *development build* (one-time):

```bash
cd day-tracker
npm install
npx eas-cli@latest login
npx eas-cli@latest build --profile development --platform android   # or ios
```

Install the build on your phone, then:

```bash
npx expo start --dev-client
```

Android maps need a Google Maps key. Put `GOOGLE_MAPS_API_KEY=...` in `day-tracker/.env` (it is git-ignored).
iPhone uses Apple Maps and needs no key.

## Code map

| File | Purpose |
|---|---|
| `src/tracker.ts` | Background location task + visit/trip detection engine |
| `src/places.ts` | Saved-place matching, OpenStreetMap lookup, re-labelling |
| `src/stats.ts` | Daily summary: timeline, commute, time breakdown |
| `src/db.ts` | On-device SQLite storage |
| `src/screens/*` | Onboarding, Today, Map, Places, Settings |

Tuning (in `src/tracker.ts`): `STAY_RADIUS_M` (100 m) and `STAY_MIN_MS` (5 min) decide what counts as a stop.

## Known limits

- Android phones from Samsung, Xiaomi, OnePlus, Vivo and Oppo may pause background apps. Set battery usage to **Unrestricted**
  (there's a button for this in the app).
- On Android, steps are **estimated** from walking distance. iPhone uses the real step counter. Exact
  Android steps would need a Health Connect integration.
- Place names come from OpenStreetMap, which is free but less complete than Google Places in some areas.
  You can always pick the right place or remember it.
