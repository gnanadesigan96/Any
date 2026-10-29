/**
 * All business settings in one place. Use Slack IDs only: channel IDs (C…/G…), member IDs (U…),
 * user-group IDs (S…). The app acts only in the channels listed here.
 *
 * Which block is used is decided by the APP_MODE environment variable:
 *   slack env add APP_MODE test        -> TEST
 *   (unset / anything else)            -> PRODUCTION
 */

export type Slot = { day: number; time: string }; // day of month + "HH:MM" local time

export type Settings = {
  mode: "production" | "test";
  utcOffsetMinutes: number; // IST = +330
  tzLabel: string;
  collectionChannel: string; // team submits here
  reviewChannel: string | null; // flagged entries for the reviewer; null = collection channel
  approvalChannel: string; // final tables + approver
  hrChannel: string | null; // HR tag; null = approval channel
  reviewer: string; // decides flagged entries, answers concerns
  approver: string; // final approval
  hrGroup: string; // user group (S…) to tag, or ""
  hrUsers: string[]; // or individual people to tag
  analyticsUsers: string[]; // the only people who may ask for comparisons / trends
  period: { startDay: number; endDay: number }; // cycle M pays startDay of M-1 .. endDay of M
  outsideWindow: "reject" | "next_cycle";
  schedule: { reminder: Slot; closingReminder: Slot | null; close: Slot };
  nudges: { everyMinutes: number; max: number; quietHours: { from: number; to: number } | null };
};

const COMMON = {
  utcOffsetMinutes: 330,
  tzLabel: "IST",
  period: { startDay: 21, endDay: 20 },
  outsideWindow: "reject" as const,
  schedule: {
    reminder: { day: 17, time: "10:00" },
    closingReminder: { day: 19, time: "10:00" },
    close: { day: 19, time: "23:59" },
  },
};

export const PRODUCTION: Settings = {
  ...COMMON,
  mode: "production",
  collectionChannel: "REPLACE-production-support-channel-id",
  reviewChannel: null,
  approvalChannel: "REPLACE-production-approval-channel-id",
  hrChannel: null,
  reviewer: "U0C2TN3B562", // Gnanadesigan
  approver: "REPLACE-poornodhaya-member-id",
  hrGroup: "",
  hrUsers: ["REPLACE-hr-member-id-or-use-hrGroup"],
  analyticsUsers: ["REPLACE-uday-member-id"],
  // Re-tag whoever a step is waiting on every 2 hours, max 3 times, not between 21:00 and 09:00.
  nudges: { everyMinutes: 120, max: 3, quietHours: { from: 21, to: 9 } },
};

export const TEST: Settings = {
  ...COMMON,
  mode: "test",
  collectionChannel: "C0CCS25TRPU", // #support-test
  reviewChannel: "C0CCS25TRPU",
  approvalChannel: "C0CCLUWT7JR", // #support-approval-test
  hrChannel: null,
  reviewer: "U0C2TN3B562", // Gnanadesigan
  approver: "U0BP446DWBD", // Manoj (test approver)
  hrGroup: "",
  hrUsers: ["U0C2TN3CC06"], // Vijay (test HR)
  analyticsUsers: ["U0BP446DWBD"], // Manoj stands in for Uday
  nudges: { everyMinutes: 10, max: 3, quietHours: null },
};

/** Rates (INR). Only a government holiday that falls on a weekday changes the rate. */
export const RATES = {
  currency: "INR",
  shift: {
    day: { weekday: 500, weekend: 1000, holiday: 1000 },
    night: { weekday: 1000, weekend: 500, holiday: 1000 },
  },
  extraTask: 500,
  weekendDays: [0, 6], // Sunday, Saturday (Date.getUTCDay numbering)
  // Add the festival holidays from the company list - only fixed-date ones are pre-filled.
  holidays: {
    "2026-01-26": "Republic Day",
    "2026-05-01": "Labour Day",
    "2026-08-15": "Independence Day",
    "2026-10-02": "Gandhi Jayanti",
    "2026-12-25": "Christmas",
    "2027-01-26": "Republic Day",
  } as Record<string, string>,
};

export function settingsFor(env: Record<string, string | undefined>): Settings {
  return (env.APP_MODE ?? "").toLowerCase() === "test" ? TEST : PRODUCTION;
}

/** Config values that are missing or not Slack IDs. */
export function problems(s: Settings): string[] {
  const out: string[] = [];
  const channel = /^[CG][A-Z0-9]{6,}$/, person = /^[UW][A-Z0-9]{6,}$/;
  for (
    const [k, v] of Object.entries({
      collectionChannel: s.collectionChannel,
      reviewChannel: s.reviewChannel,
      approvalChannel: s.approvalChannel,
      hrChannel: s.hrChannel,
    })
  ) if (v && !channel.test(v)) out.push(`${k} = ${v} (needs a channel ID like C0123ABCD)`);
  const people: Record<string, string> = { reviewer: s.reviewer, approver: s.approver };
  s.hrUsers.forEach((u, i) => people[`hrUsers[${i}]`] = u);
  s.analyticsUsers.forEach((u, i) => people[`analyticsUsers[${i}]`] = u);
  for (const [k, v] of Object.entries(people)) {
    if (!person.test(v)) out.push(`${k} = ${v} (needs a member ID like U0123ABCD)`);
  }
  if (s.hrGroup && !/^S[A-Z0-9]{6,}$/.test(s.hrGroup)) out.push(`hrGroup = ${s.hrGroup} (needs S…, or "")`);
  return out;
}
