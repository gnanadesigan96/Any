// The background location task must be registered before anything renders,
// so the OS can wake the app headlessly and deliver locations.
import './src/tracker';

import { registerRootComponent } from 'expo';
import App from './App';

registerRootComponent(App);
