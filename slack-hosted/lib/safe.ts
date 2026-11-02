/** Input validation and output sanitising shared by everything that posts to Slack. */

/** Escape text for Slack mrkdwn so it can't ping (<!channel>), mention, or hide links. */
export function esc(text: string | null | undefined): string {
  return String(text ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Clean the AI's reply before posting: no broadcast / group pings, and links shown in full
 * (so an injected "<https://evil|Approve here>" can't masquerade as something else).
 * Person mentions (<@U…>) are kept - that is how replies name people without sending names to the AI.
 */
export function sanitizeModelText(text: string): string {
  return text
    .replace(/<!(channel|here|everyone)(\|[^>]*)?>/gi, "@$1")
    .replace(/<!subteam\^[A-Z0-9]+(\|([^>]*))?>/g, "@group")
    .replace(/<!date\^[^>]*>/g, "")
    .replace(/<(https?:\/\/[^|>\s]+)\|([^>]*)>/g, "$2 ($1)")
    .replace(/<#([CG][A-Z0-9]+)(\|[^>]*)?>/g, "<#$1>");
}

export const isUserId = (v: unknown): v is string => typeof v === "string" && /^[UW][A-Z0-9]{6,}$/.test(v);
export const isChannelId = (v: unknown): v is string => typeof v === "string" && /^[CG][A-Z0-9]{6,}$/.test(v);
export const isCycleId = (v: unknown): v is string => typeof v === "string" && /^20\d{2}-(0[1-9]|1[0-2])$/.test(v);

/** Trim and cap free text (also strips control characters). */
export function clean(text: unknown, max: number): string {
  // deno-lint-ignore no-control-regex
  return String(text ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
}

export const LIMITS = {
  entriesPerRequest: 62,
  extraTask: 200,
  concern: 1500,
  response: 1500,
  dateSlackDays: 62, // dates further than this outside the period are refused outright
  mentionsPer10Min: 8,
} as const;
