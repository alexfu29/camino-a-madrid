# Camino a Madrid

A mobile-first, no-build Spanish practice tracker for Alex — a B1+ learner
doing ≤20 minutes/day of Spanish practice on the way to moving to Madrid in
January 2027. It's a single static `index.html` (vanilla HTML/CSS/JS, no
frameworks, no build step) with a built-in spaced-repetition flashcard
reviewer. Open it on your phone, log today's practice in one tap, and let
the weekly 60-minute floor — not a streak — keep you honest.

## THE ONE URL

```
https://alexfu29.github.io/camino-a-madrid/
```

Pin that URL to your phone's
home screen (Share → Add to Home Screen) — the app is configured to launch
full-screen like a native app.

## The weekly loop (≤20 min/day)

One primary activity per day plus 5′ of flashcards. The structure follows Paul
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

- **Every day — 5′ tarjetas** (the study strand). Vocab and, in Phase 1, daily
  `vosotros` drilling, via a **built-in spaced-repetition reviewer** — no
  external app, no account, no import step. Tap "repasar →" on the tracker's
  card row, grade each card **Otra vez / Bien / Fácil**, and its schedule
  (SM-2 lite) syncs across devices through the same GitHub token as the rest
  of the data. About 10 new cards a day in phase order (1 → 2 → 3), sessions
  capped at ~24 cards so they stay near 5 minutes.

  How the scheduling works: a **new card is shown twice in its first
  session** (a short learning step) before it graduates to a 1-day interval —
  one exposure followed by a whole day's gap is where most forgetting
  happens. After that, intervals run 1 day → 3 days → ×2.5 each success,
  with ±10% jitter on intervals of 4+ days so cards learned together don't
  march in lockstep and pile up on one day. New and due cards are
  **interleaved** rather than shown due-first, and the due order is reshuffled
  daily so you learn the material rather than the sequence. Seeing yesterday's
  cards again today is intentional — that 1-day gap is the point. (`deck/madrid_spanish.apkg` still exists for anyone who'd rather use
  real Anki — see "Rebuilding the deck" below.)
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
`data/stats.json` is publicly readable. It only ever contains dates,
practice minutes/task flags, and flashcard scheduling state (card-id hashes,
due dates, ease/interval numbers) — no personal content, no transcripts,
nothing sensitive. That's a deliberate tradeoff for a zero-backend,
zero-cost sync mechanism.

## Rebuilding the deck

Both the in-app reviewer and the optional Anki deck are generated from the
same source of truth, `deck/cards.csv` (90 rows: `front,back,extra,tags`,
tags space-separated with exactly one `phase1`/`phase2`/`phase3` tag plus a
category tag). Never hand-edit `cards.js` or `madrid_spanish.apkg` — edit the
CSV, run the relevant script, then commit both the CSV and the regenerated
output.

**In-app reviewer** (`cards.js`, loaded by `index.html`):

```
python deck/export_cards_js.py
```

Reads `deck/cards.csv` and writes `cards.js` at the repo root as a plain
`const CARDS = [...]` array (each card gets a stable id: an 8-hex-digit djb2
hash of its `front` text). Fails loudly — nonzero exit, clear message — on a
missing file, wrong header, a row count other than 90, a missing phase tag,
or an id collision. Workflow: edit `deck/cards.csv` → run the script →
commit both `deck/cards.csv` and `cards.js`.

**Optional Anki deck** (`madrid_spanish.apkg`, for anyone who prefers real
Anki over the built-in reviewer):

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
