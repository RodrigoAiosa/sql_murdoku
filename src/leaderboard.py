"""
Placar de detetives (leaderboard), persistido em data/leaderboard.json.

Um registro por codinome; se o mesmo codinome pontuar mais alto depois,
o registro é atualizado em vez de duplicado.
"""

import json

from src.config import LEADERBOARD_PATH


def load_leaderboard():
    if not LEADERBOARD_PATH.exists():
        return []
    try:
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_leaderboard(entries):
    try:
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def update_leaderboard(codinome, nome, avatar, total_score):
    entries = load_leaderboard()
    for e in entries:
        if e["codinome"] == codinome:
            if total_score > e["total_score"]:
                e["total_score"] = total_score
                e["nome"] = nome
                e["avatar"] = avatar
            save_leaderboard(entries)
            return
    entries.append({
        "codinome": codinome, "nome": nome, "avatar": avatar,
        "total_score": total_score,
    })
    save_leaderboard(entries)


def top_entries(limit=10):
    return sorted(load_leaderboard(), key=lambda e: -e["total_score"])[:limit]
