// Tiny in-app event bus so screens refresh the moment new locations are processed.
type Fn = () => void;
const listeners = new Set<Fn>();
export function onChange(fn: Fn): () => void {
  listeners.add(fn);
  return () => { listeners.delete(fn); };
}
export function emitChange() {
  listeners.forEach((fn) => { try { fn(); } catch {} });
}
