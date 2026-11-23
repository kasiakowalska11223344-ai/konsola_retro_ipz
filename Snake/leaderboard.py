"""Persistent local top-10 leaderboard for Snake."""

import json
from pathlib import Path

LEADERBOARD_PATH = Path(__file__).resolve().parent / "leaderboard.json"
MAX_ENTRIES = 10


def load_leaderboard():
    """Load valid leaderboard entries, returning an empty list if unavailable."""
    try:
        payload = json.loads(LEADERBOARD_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(payload, dict) or not isinstance(payload.get("scores"), list):
        return []

    entries = []
    for item in payload["scores"]:
        if not isinstance(item, dict):
            continue

        initials = item.get("initials")
        score = item.get("score")

        if (
                isinstance(initials, str)
                and len(initials) == 3
                and initials.isalpha()
                and initials.isascii()
                and isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0
        ):
            entries.append({"initials": initials.upper(), "score": score})

    entries.sort(key=lambda entry: entry["score"], reverse=True)
    return entries[:MAX_ENTRIES]


def qualifies_for_leaderboard(score, entries=None):
    """Return whether a score would enter the current top ten."""
    if entries is None:
        entries = load_leaderboard()

    if len(entries) < MAX_ENTRIES:
        return True

    return score > entries[-1]["score"]


def save_score(initials, score):
    """Save a qualifying score and return the updated leaderboard.

    Raises OSError if the leaderboard cannot be written.
    """
    initials = initials.upper()
    if len(initials) != 3 or not initials.isascii() or not initials.isalpha():
        raise ValueError("Initials must contain exactly three letters.")
    if not isinstance(score, int) or isinstance(score, bool) or score < 0:
        raise ValueError("Score must be a non-negative integer.")

    entries = load_leaderboard()
    if not qualifies_for_leaderboard(score, entries):
        return False, entries

    entries.append({"initials": initials, "score": score})
    entries.sort(key=lambda entry: entry["score"], reverse=True)
    entries = entries[:MAX_ENTRIES]

    LEADERBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = LEADERBOARD_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps({"scores": entries}, indent=4) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(LEADERBOARD_PATH)

    return True, entries
