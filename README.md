# Camino a Madrid

A mobile-first, no-build Spanish practice tracker for Alex — a B1+ learner
doing ≤20 minutes/day of Spanish practice on the way to moving to Madrid in
January 2027. It's a single static `index.html` (vanilla HTML/CSS/JS, no
frameworks, no build step) plus a small companion Anki deck. Open it on your
phone, log today's practice in one tap, and let the weekly 60-minute floor —
not a streak — keep you honest.

## THE ONE URL

```
https://alexfu29.github.io/camino-a-madrid/
```

Pin that URL to your phone's
home screen (Share → Add to Home Screen) — the app is configured to launch
full-screen like a native app.

## The weekly loop (≤20 min/day)

One primary activity per day plus 5′ of Anki. The structure follows Paul
Nation's "four strands" research — balanced time across meaning-focused
input, meaning-focused output, deliberate study, and *fluency development*
(the strand most routines skip entirely, and the one that most directly
builds speaking confidence). The tracker shows the right activity
automatically; every day is one tap to start.

| Day | Activity | Strand |
|-----|----------|--------|
| **Mon** | 8′ open conversation — Claude voice mode (topic pre-loaded) | output |
| **Tue** | 10′ listening — [Hoy Hablamos](https://open.spotify.com/show/1puKUN2oF1M5DMt8o4M1bA), daily Castilian podcast at **normal speed** | input |
| **Wed** | 9′ — **4/3/2 technique**: tell the same story 3× in 4, 3, then 2 minutes (built-in timer). Replicated gains in fluency *and* accuracy | fluency |
| **Thu** | 8′ roleplay — [Gliglish](https://gliglish.com), always **"Spanish (Spain)"** (free tier: 10 min/day) | output |
| **Fri** | 8′ shadowing — [Español con Juan](https://www.youtube.com/@EspanolconJuan/videos): repeat ~1 min aloud *simultaneously*, 3 passes | fluency + ear |
| **Sat** | Free — conversation or catch-up | output |
| **Sun** | Rest, or minimum day. Weekly check-in arrives at 7pm | — |

- **Every day — 5′ Anki** (the study strand). Vocab and, in Phase 1, daily
  `vosotros` drilling. The tracker's "abrir →" link opens
  [AnkiWeb](https://ankiweb.net/decks) — for it to have your cards, import
  `madrid_spanish.apkg` into Anki once and enable AnkiWeb sync (free account).
- **Minimum viable day (bad-day fallback) — 3′.** 5 flashcards + one sentence
  said out loud. Counts. Better than zero.

Why listening at natural speed matters: the standard arrival shock isn't
failing to speak — it's failing to *understand*, because learner audio runs at
60–80% of real speed while Madrid runs at 170–190 wpm. Tue trains that
directly and Fri's shadowing converts it into speech rhythm.

## Weekly rules

- **60′ floor, 90′ target**, resetting every Monday.
- **No streaks, anywhere in this app, by design.** A missed day or even a
  missed week doesn't break anything — the only unit of accountability is
  "did this week clear the floor." Streak mechanics reward showing up over
  substance and produce all-or-nothing guilt spirals; a weekly floor doesn't.

## Setup: the GitHub sync token

Sync is optional — the tracker works entirely offline via `localStorage` with
zero setup. To sync your practice data across devices (phone + laptop) via
this repo's `data/stats.json`:

1. Go to **github.com/settings/personal-access-tokens → New token**.
2. **Scope it to only this repository** (`camino-a-madrid`), not all repos.
3. Under **Repository permissions → Contents**, set **Read and write**.
   Leave everything else as "No access."
4. Copy the generated token (`github_pat_…`).
5. Open the tracker → gear icon → paste the token into **Settings**.
   Do this on every device, including your phone.

The token is stored only in that device's `localStorage` (`camino-pat`) — it
is never sent anywhere except directly to `api.github.com`.

## Recovery playbook

- **Lost your PAT?** Generate a new one (same steps above) and paste it in on
  each device again. The old one can be revoked from the GitHub settings page.
- **New device?** Open the URL, gear icon, paste the token. It'll pull and
  merge `data/stats.json` automatically.
- **Missed days or whole weeks?** Nothing breaks. Just resume — there's no
  streak to lose.
- **Sync banner is red?** The tracker still works completely locally
  (`localStorage`); fix the token/owner/repo in Settings when convenient, then
  hit "Probar sincronización" to retry. Nothing you log is lost while it's
  red — sync failures never block or clear local data.
- **No token at all, ever?** Use **Exportar JSON** / **Importar JSON** in
  Settings as a manual, PAT-free backup/restore path between devices.

## A note on `data/stats.json` being public

If this repo is public (as GitHub Pages typically requires on the free tier),
`data/stats.json` is publicly readable. It only ever contains dates and
practice minutes/task flags — no personal content, no transcripts, nothing
sensitive. That's a deliberate tradeoff for a zero-backend, zero-cost sync
mechanism.

## Rebuilding the Anki deck

```
pip install genanki
python deck/build_deck.py
```

This reads `deck/cards.csv` and writes `madrid_spanish.apkg` at the repo root,
with three subdecks — `Madrid Spanish::1 Reboot`, `::2 Expansión`,
`::3 Simulación Madrid` — split by the `phase1`/`phase2`/`phase3` tag on each
row. Re-running it after editing `cards.csv` updates existing notes in place
rather than duplicating them (note GUIDs are derived from the front field).
Import the resulting `madrid_spanish.apkg` into Anki (desktop or AnkiMobile)
as usual.
