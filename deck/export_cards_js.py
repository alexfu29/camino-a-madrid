#!/usr/bin/env python3
"""
export_cards_js.py — builds cards.js (repo root) from deck/cards.csv.

Usage:
    python deck/export_cards_js.py

Reads deck/cards.csv (columns: front,back,extra,tags — tags space-separated,
must include exactly one of phase1/phase2/phase3 plus one category tag) and
writes cards.js at the repository root as:

    const CARDS = [
      {id: "1a2b3c4d", front: "...", back: "...", extra: "...", phase: 1, tags: ["phase1","vosotros"]},
      ...
    ];

so it can be loaded the same way as prompts.js: <script src="cards.js"></script>,
read as the global CARDS array.

ID ALGORITHM (documented here and in the header of the generated cards.js):
    Each card's `id` is an 8-hex-digit djb2 hash of its (stripped) `front`
    field, computed as:

        h = 5381
        for each character c in front:
            h = ((h * 33) + ord(c)) & 0xFFFFFFFF
        id = lowercase hex of h, zero-padded to 8 digits

    This is the classic djb2 string hash (Bernstein), truncated to 32 bits.
    It's deterministic and stable across reruns as long as the front text
    doesn't change — editing `back`/`extra`/`tags` never changes a card's id,
    but editing `front` mints a new id (same tradeoff build_deck.py makes with
    genanki.guid_for(front)).

    Collisions across the 90 fronts are checked below and are FATAL — if two
    different fronts hash to the same 8 hex digits, the script refuses to
    write cards.js and exits nonzero. (32 bits over 90 items has a collision
    probability far below one in a million, so a real collision here would
    mean either a bug in this script or truly pathological input.)

Fails with a clear, nonzero-exit error if:
    - cards.csv is missing
    - the CSV header doesn't match front,back,extra,tags
    - the number of data rows is not exactly 90
    - any row is missing a phase1/phase2/phase3 tag (or has more than one)
    - two different fronts collide on their computed id
"""

import csv
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "deck", "cards.csv")
OUTPUT_PATH = os.path.join(REPO_ROOT, "cards.js")

EXPECTED_COLUMNS = ["front", "back", "extra", "tags"]
EXPECTED_ROW_COUNT = 90

PHASE_TAGS = {"phase1": 1, "phase2": 2, "phase3": 3}


def fail(message):
    sys.stderr.write("ERROR: " + message + "\n")
    sys.exit(1)


def djb2_hash8(s):
    """8-hex-digit djb2 hash of a string. See module docstring for the algorithm."""
    h = 5381
    for ch in s:
        h = ((h * 33) + ord(ch)) & 0xFFFFFFFF
    return "%08x" % h


def load_rows():
    if not os.path.isfile(CSV_PATH):
        fail("cards.csv not found at " + CSV_PATH)

    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        if header is None:
            fail("cards.csv is empty.")
        normalized = [h.strip().lower() for h in header]
        if normalized != EXPECTED_COLUMNS:
            fail(
                "cards.csv has the wrong columns.\n"
                "  expected: " + ",".join(EXPECTED_COLUMNS) + "\n"
                "  found:    " + ",".join(header)
            )
        rows = list(reader)

    if len(rows) != EXPECTED_ROW_COUNT:
        fail(
            "cards.csv has %d data rows; expected exactly %d."
            % (len(rows), EXPECTED_ROW_COUNT)
        )

    for i, row in enumerate(rows, start=2):  # row 1 is the header
        front = (row.get("front") or "").strip()
        back = (row.get("back") or "").strip()
        tags_raw = (row.get("tags") or "").strip()

        if not front:
            fail("row %d: 'front' is empty." % i)
        if not back:
            fail("row %d: 'back' is empty." % i)
        if not tags_raw:
            fail("row %d: 'tags' is empty (front=%r) — every row needs a phase1/phase2/phase3 tag." % (i, front))

        tags = tags_raw.split()
        phase_tags_present = [t for t in tags if t in PHASE_TAGS]
        if not phase_tags_present:
            fail(
                "row %d: no phase tag found in tags %r (front=%r). "
                "Every row must include one of: phase1, phase2, phase3." % (i, tags, front)
            )
        if len(phase_tags_present) > 1:
            fail(
                "row %d: multiple phase tags found %r (front=%r) — exactly one expected."
                % (i, phase_tags_present, front)
            )

    return rows


def build_cards(rows):
    cards = []
    seen_ids = {}  # id -> front (first one seen), to detect collisions
    for row in rows:
        front = row["front"].strip()
        back = row["back"].strip()
        extra = (row.get("extra") or "").strip()
        tags = row["tags"].strip().split()
        phase_key = next(t for t in tags if t in PHASE_TAGS)
        phase = PHASE_TAGS[phase_key]

        card_id = djb2_hash8(front)
        if card_id in seen_ids and seen_ids[card_id] != front:
            fail(
                "id collision: %r and %r both hash to %s. "
                "Edit one of the fronts to disambiguate and rerun."
                % (seen_ids[card_id], front, card_id)
            )
        seen_ids[card_id] = front

        cards.append({
            "id": card_id,
            "front": front,
            "back": back,
            "extra": extra,
            "phase": phase,
            "tags": tags,
        })
    return cards


def render_js(cards):
    lines = []
    lines.append("// Camino a Madrid — SRS flashcard deck, generated from deck/cards.csv.")
    lines.append('// Loaded via <script src="cards.js"></script>; CARDS is read as a global.')
    lines.append("// DO NOT EDIT BY HAND — regenerate with: python deck/export_cards_js.py")
    lines.append("//")
    lines.append("// `id` is an 8-hex-digit djb2 hash of the (stripped) `front` field:")
    lines.append("//   h = 5381; for each char c in front: h = ((h*33) + ord(c)) & 0xFFFFFFFF")
    lines.append("//   id = lowercase hex of h, zero-padded to 8 digits")
    lines.append("// Collisions across all fronts are checked at generation time (fatal if found).")
    lines.append("const CARDS = [")
    for c in cards:
        entry = (
            "  {id: " + json.dumps(c["id"]) +
            ", front: " + json.dumps(c["front"], ensure_ascii=False) +
            ", back: " + json.dumps(c["back"], ensure_ascii=False) +
            ", extra: " + json.dumps(c["extra"], ensure_ascii=False) +
            ", phase: " + str(c["phase"]) +
            ", tags: " + json.dumps(c["tags"], ensure_ascii=False) +
            "},"
        )
        lines.append(entry)
    lines.append("];")
    lines.append("")
    return "\n".join(lines)


def main():
    rows = load_rows()
    cards = build_cards(rows)
    js = render_js(cards)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    print("Wrote %s (%d cards)." % (OUTPUT_PATH, len(cards)))


if __name__ == "__main__":
    main()
