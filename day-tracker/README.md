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

## Install it on your phone

### Android: download the APK (no developer tools needed)

Every push to this repository builds the app automatically (GitHub Actions →
*Day Tracker – Android APK*) and publishes it on the repository's **Releases** page.

1. On your Android phone, open `https://github.com/<owner>/<repo>/releases/latest`.
2. Tap **DayTracker.apk** to download it.
3. Open the downloaded file. If Android asks, allow your browser to *install unknown apps*.
4. Open Day Tracker and follow the setup screens.

New builds install over the old one and keep your data.

**Optional key** (repository → Settings → Secrets and variables → Actions): `GOOGLE_PLACES_API_KEY`
gives better restaurant and shop names (Google Places API (New): free monthly allowance, then paid).
The app works fully without it.

### iPhone

Apple only lets you install apps through the App Store or TestFlight, and both need a paid Apple Developer
account ($99/year). With one:

```bash
cd day-tracker
npx eas-cli@latest build --platform ios --profile production
npx eas-cli@latest submit --platform ios   # then install via TestFlight
```

### Developers: live-reload build

```bash
cd day-tracker && npm install
npx expo run:android      # needs Android Studio, or use: npx eas-cli build --profile development
```

## Maps

Day Tracker has its own map. It's drawn on the phone by **MapLibre** (open source) from
**OpenStreetMap** data, served free by **OpenFreeMap**. It doesn't use Google and needs no API key.
Routes, place pins and place circles are drawn by the app (`src/components/AppMap.tsx`). The map follows the
phone's light/dark mode. To restyle the whole map, point `STYLE_LIGHT` / `STYLE_DARK` at your own
[MapLibre style](https://maplibre.org/maplibre-style-spec/).

## Code map

| File | Purpose |
|---|---|
| `src/tracker.ts` | Background location task + visit/trip detection engine |
| `src/places.ts` | Saved-place matching, OpenStreetMap lookup, re-labelling |
| `src/stats.ts` | Daily summary: timeline, commute, time breakdown |
| `src/db.ts` | On-device SQLite storage |
| `src/components/AppMap.tsx` | Our own map (MapLibre + OpenStreetMap) |
| `src/screens/*` | Onboarding, Today, Map, Places, Settings |

Tuning (in `src/tracker.ts`): `STAY_RADIUS_M` (100 m) and `STAY_MIN_MS` (5 min) decide what counts as a stop.

## Reliability features

- **Steps:** iPhone uses the motion chip. Android uses **Health Connect**, which gets steps from the phone,
  Google Fit, Samsung Health or a watch. If neither is available, steps are estimated from walking distance,
  and the app says so.
- **Battery killers:** the app opens Android's own "allow background" dialog and shows extra steps for your
  phone's brand (Samsung, Xiaomi, OnePlus, Vivo, Oppo, Huawei).
- **Self-healing:** a watchdog restarts tracking if it stops. Geofences around your saved places wake the app
  on arrival or departure even after the phone killed it. Any gap is shown on the Today screen.
- **Place names:** Google Places (if a key is set) plus OpenStreetMap. Any name you choose is remembered for that spot.
- **Travel mode:** speed, plus steps during the trip (about 100 steps/min means walking, almost none means a
  vehicle), plus your own corrections between the same places.

Still out of an app's control: if you swipe the app away on an iPhone, iOS stops it until you open it again
or arrive at or leave a saved place. Health Connect only has steps if something writes them (the phone on
Android 14+, Google Fit, Samsung Health or a watch).
