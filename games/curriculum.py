"""
curriculum.py
-------------
LK20 competence-goal mapping for Math Practice.

The goal of this module is to let the parent report honestly tell a Norwegian
parent or teacher which LK20 competence goals the app has evidence for.

Design principles
-----------------
* Norwegian text stored verbatim from udir.no — do not paraphrase.
* Each goal declares which game_ids supply evidence for it, and which
  achievement tier counts as mastery.
* Goals the app does not yet cover are declared with covers=[]. They render
  as "Ikke påbegynt i appen" — an honest label that turns a gap into a
  forward-looking statement.
* To add a new game family later (equations, probability, time, word
  problems), only edit this file: either attach new game_ids to existing
  goals, or flip covers=[] to a populated list as coverage ships.

Goal statuses
-------------
    "mestret"         — Sharp-or-higher in ALL covering games (green)
    "under_utvikling" — has played at least one covering game, not yet mestret (amber)
    "ikke_startet"    — covered by app but not yet played (grey)
    "ikke_i_appen"    — not yet covered by any game (grey, honest label)
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.


# ── Goal definitions ──────────────────────────────────────────────────────────
#
# threshold: "sharp" | "precise" | "flawless"
#   "sharp"    — first tier, achievable after one strong session
#   "precise"  — consistent high accuracy
#   "flawless" — perfect session
#
# Use "sharp" for core curriculum goals (we want mastery reachable through
# normal play) and reserve "precise" for demanding goals.

GOALS_5_TRINN: list[dict] = [
    {
        "id": "g1_fr_des_prosent",
        "text": ("Utforske og forklare sammenhenger mellom brøker, desimaltall "
                 "og prosent og bruke det i hoderegning."),
        "covers":    ["conv_basic", "conv_intermediate", "conv_advanced"],
        "threshold": "sharp",
    },
    {
        "id": "g2_brok_representasjon",
        "text": ("Beskrive brøk som del av en hel, som del av en mengde og "
                 "som tall på tallinjen og vurdere og navngi størrelsene."),
        # The app tests fraction arithmetic but not visual/number-line
        # representation yet. Tutorial slideshow (v0.7) will close this gap;
        # until then we honestly label it as partial-coverage via frac_basic.
        "covers":    ["frac_basic"],
        "threshold": "sharp",
        "note":      "Appen tester brøkregning. Visuell representasjon og "
                     "tallinje kommer i en senere versjon.",
    },
    {
        "id": "g3_brok_representasjoner_oversette",
        "text": ("Representere brøker på ulike måter og oversette mellom de "
                 "ulike representasjonene."),
        # Conv family is the primary vehicle for representation-translation.
        "covers":    ["conv_basic", "conv_intermediate", "conv_advanced"],
        "threshold": "sharp",
    },
    {
        "id": "g4_strategier_regning",
        "text": ("Utvikle og bruke ulike strategier for regning med positive "
                 "tall og brøk og forklare tenkemåtene sine."),
        # Broad goal — all core arithmetic families provide evidence.
        "covers":    ["mult_basic", "mult_intermediate", "mult_advanced",
                      "div_basic",  "div_intermediate",  "div_advanced",
                      "frac_basic", "frac_intermediate", "frac_advanced"],
        "threshold": "sharp",
        "note":      "Appen dokumenterer regneferdighet. Muntlig forklaring "
                     "av tenkemåter hører hjemme i klasserommet.",
    },
    {
        "id": "g5_brok_hverdagsproblemer",
        "text": ("Formulere og løse problemer fra egen hverdag som har med "
                 "brøk å gjøre."),
        "covers":    [],   # no word-problem game yet
        "threshold": "sharp",
        "note":      "Tekstoppgaver med brøk er planlagt i en senere versjon.",
    },
    {
        "id": "g6_sannsynlighet",
        "text": ("Diskutere tilfeldighet og sannsynlighet i spill og "
                 "praktiske situasjoner og knytte det til brøk."),
        "covers":    [],   # no probability game yet
        "threshold": "sharp",
        "note":      "Sannsynlighet og enkel kombinatorikk er planlagt i en "
                     "senere versjon.",
    },
    {
        "id": "g7_ligninger",
        "text": ("Løse ligninger og ulikheter gjennom logiske resonnementer "
                 "og forklare hva det vil si at et tall er en løsning på en "
                 "ligning."),
        "covers":    [],   # no equations game yet
        "threshold": "sharp",
        "note":      "Ligninger og ulikheter er planlagt i en senere versjon.",
    },
    # NOTE: goal 8 (regneark/personlig økonomi) and goal 10 (programmering)
    # are intentionally omitted — out of scope for this math-drill product.
    {
        "id": "g9_tid_hverdagsproblemer",
        "text": ("Formulere og løse problemer fra egen hverdag som har med "
                 "tid å gjøre."),
        "covers":    [],   # no time word-problem game yet
        "threshold": "sharp",
        "note":      "Tekstoppgaver med tid er planlagt i en senere versjon.",
    },
]


# ── Status resolver ───────────────────────────────────────────────────────────

def _achievement_id(tier: str, game_id: str) -> str:
    """Return the achievement id string used in achievements.py."""
    return f"{tier}_{game_id}"


def goal_status(goal: dict, ach_store, sessions_store) -> dict:
    """Resolve a single goal's status from the stores.

    Returns a dict:
        {
          "status":   "mestret" | "under_utvikling" | "ikke_startet" | "ikke_i_appen",
          "progress": (mastered_count, total_covering_games),
          "detail":   Norwegian short note (optional),
        }
    """
    covers = list(goal.get("covers", []))
    threshold = goal.get("threshold", "sharp")
    note = goal.get("note", "")

    # Case 1: the app does not cover this goal at all
    if not covers:
        return {
            "status":   "ikke_i_appen",
            "progress": (0, 0),
            "detail":   note or "Dekkes ikke av appen i denne versjonen.",
        }

    earned = set(ach_store.get_earned())
    played = {s.get("game_id", "") for s in sessions_store.all_sessions()} \
             if sessions_store else set()

    mastered = 0
    any_played = False
    for gid in covers:
        if gid in played:
            any_played = True
        if _achievement_id(threshold, gid) in earned:
            mastered += 1

    total = len(covers)
    if mastered == total:
        status = "mestret"
    elif any_played or mastered > 0:
        status = "under_utvikling"
    else:
        status = "ikke_startet"

    return {
        "status":   status,
        "progress": (mastered, total),
        "detail":   note,
    }


# ── Display helpers ───────────────────────────────────────────────────────────

STATUS_LABEL_NO = {
    "mestret":          "Mestret",
    "under_utvikling":  "Under utvikling",
    "ikke_startet":     "Ikke startet",
    "ikke_i_appen":     "Ikke påbegynt i appen",
}

# RGB tuples (0..1) for PDF / tk
STATUS_COLOR_RGB = {
    "mestret":          (0.08, 0.50, 0.24),   # #15803d green
    "under_utvikling":  (0.96, 0.62, 0.04),   # #f59e0b amber
    "ikke_startet":     (0.58, 0.64, 0.72),   # #94a3b8 dim
    "ikke_i_appen":     (0.74, 0.78, 0.83),   # #bdc5d0 fainter dim
}


def summary_counts(ach_store, sessions_store) -> dict:
    """Aggregate counts for the narrative ('2 av 8 mestret, 2 under utvikling')."""
    counts = {"mestret": 0, "under_utvikling": 0,
              "ikke_startet": 0, "ikke_i_appen": 0}
    for goal in GOALS_5_TRINN:
        st = goal_status(goal, ach_store, sessions_store)["status"]
        counts[st] += 1
    counts["total"] = len(GOALS_5_TRINN)
    return counts


def weakest_game_ids(sessions_store, limit: int = 1) -> list[str]:
    """Return game_ids the student struggles most with (lowest avg accuracy,
    minimum 2 sessions)."""
    if not sessions_store:
        return []
    summary = sessions_store.per_game_summary()
    candidates = [(gid, row["avg_accuracy"])
                  for gid, row in summary.items()
                  if row["sessions"] >= 2]
    candidates.sort(key=lambda t: t[1])
    return [gid for gid, _ in candidates[:limit]]


def strongest_game_ids(sessions_store, limit: int = 1) -> list[str]:
    """Return game_ids with highest avg accuracy (minimum 2 sessions)."""
    if not sessions_store:
        return []
    summary = sessions_store.per_game_summary()
    candidates = [(gid, row["avg_accuracy"])
                  for gid, row in summary.items()
                  if row["sessions"] >= 2]
    candidates.sort(key=lambda t: -t[1])
    return [gid for gid, _ in candidates[:limit]]
