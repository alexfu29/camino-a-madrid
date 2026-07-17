#!/usr/bin/env python3
"""
build_deck.py — builds madrid_spanish.apkg from deck/cards.csv.

Usage:
    pip install genanki
    python deck/build_deck.py

Reads deck/cards.csv (columns: front,back,extra,tags — tags space-separated,
must include one of phase1/phase2/phase3) and writes madrid_spanish.apkg at
the repository root, with three subdecks split by phase tag:

    Madrid Spanish::1 Reboot
    Madrid Spanish::2 Expansión
    Madrid Spanish::3 Simulación Madrid

Rebuild-safe: note GUIDs are derived from the front field
(genanki.guid_for(front)), so re-running this script after editing cards.csv
updates existing notes instead of duplicating them.

Fails with a clear, nonzero-exit error if:
    - cards.csv is missing
    - the CSV header doesn't match front,back,extra,tags
    - any row is missing a phase1/phase2/phase3 tag
"""

import csv
import os
import sys

try:
    import genanki
except ImportError:
    sys.stderr.write(
        "ERROR: the 'genanki' package is required.\n"
        "Install it with:  pip install genanki\n"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Fixed IDs — keep these constant across rebuilds so Anki treats reruns as
# updates to the same model/decks rather than creating new ones.
# ---------------------------------------------------------------------------
MODEL_ID = 1607392319001
DECK_ID_ROOT = 1607392319010
DECK_ID_PHASE1 = 1607392319011
DECK_ID_PHASE2 = 1607392319012
DECK_ID_PHASE3 = 1607392319013

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "deck", "cards.csv")
OUTPUT_PATH = os.path.join(REPO_ROOT, "madrid_spanish.apkg")

EXPECTED_COLUMNS = ["front", "back", "extra", "tags"]

PHASE_TAGS = {
    "phase1": ("Madrid Spanish::1 Reboot", DECK_ID_PHASE1),
    "phase2": ("Madrid Spanish::2 Expansión", DECK_ID_PHASE2),
    "phase3": ("Madrid Spanish::3 Simulación Madrid", DECK_ID_PHASE3),
}

CARD_CSS = """
.card {
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    font-size: 22px;
    line-height: 1.4;
    text-align: center;
    color: #0b0b0b;
    background-color: #fcfcfb;
    padding: 24px 16px;
}
.front {
    font-size: 26px;
    font-weight: 600;
}
hr#answer {
    border: none;
    border-top: 1px solid #e1e0d9;
    margin: 18px 0;
}
.back {
    font-size: 24px;
    font-weight: 500;
}
.extra {
    margin-top: 14px;
    font-size: 17px;
    color: #52514e;
}
@media (prefers-color-scheme: dark) {
    .card { color: #ffffff; background-color: #1a1a19; }
    hr#answer { border-top-color: #2c2c2a; }
    .extra { color: #c3c2b7; }
}
"""

MODEL = genanki.Model(
    MODEL_ID,
    "Madrid Spanish Basic",
    fields=[
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Extra"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="front">{{Front}}</div>',
            "afmt": (
                '<div class="front">{{Front}}</div>'
                '<hr id="answer">'
                '<div class="back">{{Back}}</div>'
                '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}'
            ),
        },
    ],
    css=CARD_CSS,
)


def fail(message):
    sys.stderr.write("ERROR: " + message + "\n")
    sys.exit(1)


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

    if not rows:
        fail("cards.csv has no data rows.")

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


def build():
    rows = load_rows()

    root_deck = genanki.Deck(DECK_ID_ROOT, "Madrid Spanish")
    subdecks = {
        key: genanki.Deck(deck_id, name)
        for key, (name, deck_id) in PHASE_TAGS.items()
    }

    package_decks = [root_deck] + list(subdecks.values())

    for row in rows:
        front = row["front"].strip()
        back = row["back"].strip()
        extra = (row.get("extra") or "").strip()
        tags = row["tags"].strip().split()
        phase_key = next(t for t in tags if t in PHASE_TAGS)

        note = genanki.Note(
            model=MODEL,
            fields=[front, back, extra],
            tags=tags,
            guid=genanki.guid_for(front),
        )
        subdecks[phase_key].add_note(note)

    package = genanki.Package(package_decks)
    package.write_to_file(OUTPUT_PATH)
    print("Wrote %s (%d notes across %d subdecks)." % (OUTPUT_PATH, len(rows), len(subdecks)))


if __name__ == "__main__":
    build()
