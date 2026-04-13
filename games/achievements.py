"""
achievements.py
---------------
All achievement definitions for Math Practice.

Each achievement dict:
    id          unique string key
    name        display name (shown in popup and achievements screen)
    desc        one-line description
    points      points awarded on unlock
    icon        emoji
    hidden      True -> shown as "???" until earned
    category    grouping label in the achievements screen
    game_id     set on per-game achievements (for sub-grouping in UI)
    when        "live"  -> checked after every correct answer (streaks, speed)
                "end"   -> checked when a game session ends (everything else)
    check       fn(store_stats, ctx) -> bool
                  store_stats: AchievementsStore.get_stats() — already updated for "end"
                  ctx:  {"session_streak", "speed_demon", "session_correct"} for live
                        {"session_minutes"} for end
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

# ── constants ──────────────────────────────────────────────────────────────────

GAME_IDS = [
    "mult_basic", "mult_intermediate", "mult_advanced",
    "div_basic",  "div_intermediate",  "div_advanced",
]

GAME_NAMES = {
    "mult_basic":        "Multiplication: Beginner",
    "mult_intermediate": "Multiplication: Intermediate",
    "mult_advanced":     "Multiplication: Advanced",
    "div_basic":         "Division: Beginner",
    "div_intermediate":  "Division: Intermediate",
    "div_advanced":      "Division: Advanced",
}

GAME_SHORT = {
    "mult_basic":        "Mult. Beginner",
    "mult_intermediate": "Mult. Intermediate",
    "mult_advanced":     "Mult. Advanced",
    "div_basic":         "Div. Beginner",
    "div_intermediate":  "Div. Intermediate",
    "div_advanced":      "Div. Advanced",
}

# Which achievement unlocks each intermediate / advanced game
UNLOCK_REQUIREMENTS = {
    "mult_intermediate": "sharp_mult_basic",
    "mult_advanced":     "sharp_mult_intermediate",
    "div_intermediate":  "sharp_div_basic",
    "div_advanced":      "sharp_div_intermediate",
}


# ── helper ─────────────────────────────────────────────────────────────────────

def _pg(stats, game_id, field, default=0):
    """Safely read a per_game stat."""
    return stats.get("per_game", {}).get(game_id, {}).get(field, default)


# ── builder ────────────────────────────────────────────────────────────────────

def _build_achievements():
    achs = []

    # ── Milestones ─────────────────────────────────────────────────────────────
    achs += [
        dict(id="first_correct",  name="First Step",    icon="👣",
             desc="Get your very first correct answer.",
             points=10,  hidden=False, category="Milestones", when="live",
             check=lambda s, c: (s.get("total_correct", 0) == 0
                                 and c.get("session_correct", 0) >= 1)),

        dict(id="milestone_25",   name="Warming Up",    icon="🔥",
             desc="Answer 25 questions correctly in total.",
             points=25,  hidden=False, category="Milestones", when="end",
             check=lambda s, c: s.get("total_correct", 0) >= 25),

        dict(id="milestone_100",  name="Century",       icon="💯",
             desc="Answer 100 questions correctly in total.",
             points=50,  hidden=False, category="Milestones", when="end",
             check=lambda s, c: s.get("total_correct", 0) >= 100),

        dict(id="milestone_500",  name="Five Hundred",  icon="⭐",
             desc="Answer 500 questions correctly in total.",
             points=200, hidden=False, category="Milestones", when="end",
             check=lambda s, c: s.get("total_correct", 0) >= 500),

        dict(id="milestone_1000", name="One Thousand",  icon="🌟",
             desc="Answer 1000 questions correctly in total.",
             points=500, hidden=False, category="Milestones", when="end",
             check=lambda s, c: s.get("total_correct", 0) >= 1000),
    ]

    # ── Streaks ────────────────────────────────────────────────────────────────
    achs += [
        dict(id="streak_5",  name="On a Roll",    icon="🔗",
             desc="Get 5 correct answers in a row.",
             points=25,  hidden=False, category="Streaks", when="live",
             check=lambda s, c: c.get("session_streak", 0) >= 5),

        dict(id="streak_10", name="Hot Streak",   icon="🔥",
             desc="Get 10 correct answers in a row.",
             points=75,  hidden=False, category="Streaks", when="live",
             check=lambda s, c: c.get("session_streak", 0) >= 10),

        dict(id="streak_20", name="Unstoppable",  icon="⚡",
             desc="Get 20 correct answers in a row.",
             points=200, hidden=False, category="Streaks", when="live",
             check=lambda s, c: c.get("session_streak", 0) >= 20),

        dict(id="streak_50", name="Legendary",    icon="🏆",
             desc="Get 50 correct answers in a row.",
             points=500, hidden=False, category="Streaks", when="live",
             check=lambda s, c: c.get("session_streak", 0) >= 50),
    ]

    # ── Per-game achievements ──────────────────────────────────────────────────
    for gid in GAME_IDS:
        gname = GAME_NAMES[gid]
        short = GAME_SHORT[gid]

        achs.append(dict(
            id=f"first_win_{gid}",
            name=f"First Win",
            icon="🎮",
            desc=f"Complete a session of {gname} with 10+ attempts.",
            points=15, hidden=False,
            category="Game Mastery", game_id=gid,
            when="end",
            check=(lambda s, c, g=gid: _pg(s, g, "best_attempts") >= 10),
        ))
        achs.append(dict(
            id=f"sharp_{gid}",
            name=f"Sharp",
            icon="🎯",
            desc=f"Score 80%+ accuracy in {gname} with 10+ attempts.",
            points=50, hidden=False,
            category="Game Mastery", game_id=gid,
            when="end",
            check=(lambda s, c, g=gid:
                   _pg(s, g, "best_attempts") >= 10
                   and _pg(s, g, "best_accuracy") >= 80),
        ))
        achs.append(dict(
            id=f"precise_{gid}",
            name=f"Precise",
            icon="🏹",
            desc=f"Score 90%+ accuracy in {gname} with 10+ attempts.",
            points=100, hidden=False,
            category="Game Mastery", game_id=gid,
            when="end",
            check=(lambda s, c, g=gid:
                   _pg(s, g, "best_attempts") >= 10
                   and _pg(s, g, "best_accuracy") >= 90),
        ))
        achs.append(dict(
            id=f"flawless_{gid}",
            name=f"Flawless",
            icon="💎",
            desc=f"Score 100% accuracy in {gname} with 10+ attempts.",
            points=250, hidden=False,
            category="Game Mastery", game_id=gid,
            when="end",
            check=(lambda s, c, g=gid:
                   _pg(s, g, "best_attempts") >= 10
                   and _pg(s, g, "best_accuracy") >= 100),
        ))

    # ── Missed queue ───────────────────────────────────────────────────────────
    achs += [
        dict(id="missed_attempted", name="Facing Fears", icon="😤",
             desc="Open the Practice Missed game for the first time.",
             points=10,  hidden=False, category="Practice", when="end",
             check=lambda s, c: s.get("missed_attempted", False)),

        dict(id="missed_resilient", name="Resilient",    icon="💪",
             desc="Answer a previously missed question correctly.",
             points=25,  hidden=False, category="Practice", when="end",
             check=lambda s, c: s.get("missed_resilient", False)),

        dict(id="missed_cleared",   name="Clean Slate",  icon="✨",
             desc="Clear the entire missed questions queue.",
             points=100, hidden=False, category="Practice", when="end",
             check=lambda s, c: s.get("missed_cleared", False)),
    ]

    # ── Exploration ────────────────────────────────────────────────────────────
    achs += [
        dict(id="explore_3",   name="Curious",       icon="🔭",
             desc="Play 3 different games.",
             points=30,  hidden=False, category="Exploration", when="end",
             check=lambda s, c: len(s.get("games_played", [])) >= 3),

        dict(id="explore_all", name="Well Rounded",  icon="🌐",
             desc="Play all 6 main games at least once.",
             points=100, hidden=False, category="Exploration", when="end",
             check=lambda s, c: len(s.get("games_played", [])) >= 6),

        dict(id="master_all",  name="Master of All", icon="👑",
             desc="Achieve 80%+ accuracy in all 6 main games.",
             points=500, hidden=False, category="Exploration", when="end",
             check=lambda s, c: all(
                 _pg(s, gid, "best_accuracy") >= 80
                 and _pg(s, gid, "best_attempts") >= 10
                 for gid in GAME_IDS
             )),
    ]

    # ── Dedication ─────────────────────────────────────────────────────────────
    achs += [
        dict(id="daily_5",  name="Daily Grind",  icon="📅",
             desc="Play on 5 different days.",
             points=50,  hidden=False, category="Dedication", when="end",
             check=lambda s, c: len(s.get("days_played", [])) >= 5),

        dict(id="daily_10", name="Consistent",   icon="🗓",
             desc="Play on 10 different days.",
             points=150, hidden=False, category="Dedication", when="end",
             check=lambda s, c: len(s.get("days_played", [])) >= 10),

        dict(id="daily_30", name="Devoted",      icon="🏅",
             desc="Play on 30 different days.",
             points=500, hidden=False, category="Dedication", when="end",
             check=lambda s, c: len(s.get("days_played", [])) >= 30),
    ]

    # ── Leaderboard ────────────────────────────────────────────────────────────
    achs += [
        dict(id="lb_top3",   name="Podium",           icon="🥉",
             desc="Reach top 3 on any leaderboard.",
             points=75,  hidden=False, category="Leaderboard", when="end",
             check=lambda s, c: any(v <= 3 for v in s.get("lb_positions", {}).values())),

        dict(id="lb_top1",   name="Top of the Class", icon="🥇",
             desc="Reach #1 on any leaderboard.",
             points=150, hidden=False, category="Leaderboard", when="end",
             check=lambda s, c: any(v == 1 for v in s.get("lb_positions", {}).values())),

        dict(id="lb_triple", name="Hall of Fame",     icon="🎖",
             desc="Hold a top-3 spot on three different leaderboards.",
             points=300, hidden=False, category="Leaderboard", when="end",
             check=lambda s, c: sum(
                 1 for v in s.get("lb_positions", {}).values() if v <= 3
             ) >= 3),
    ]

    # ── Hidden / secrets ───────────────────────────────────────────────────────
    achs += [
        dict(id="speed_demon", name="Speed Demon", icon="⚡",
             desc="Answer 10 questions correctly in under 60 seconds.",
             points=100, hidden=True, category="Secrets", when="live",
             check=lambda s, c: c.get("speed_demon", False)),

        dict(id="night_owl",   name="Night Owl",   icon="🦉",
             desc="Play after 9 PM.",
             points=25,  hidden=True, category="Secrets", when="end",
             check=lambda s, c: s.get("night_owl", False)),

        dict(id="early_bird",  name="Early Bird",  icon="🐦",
             desc="Play before 7 AM.",
             points=25,  hidden=True, category="Secrets", when="end",
             check=lambda s, c: s.get("early_bird", False)),

        dict(id="the_grind",   name="The Grind",   icon="⏰",
             desc="Play for 30 minutes in a single session.",
             points=100, hidden=True, category="Secrets", when="end",
             check=lambda s, c: c.get("session_minutes", 0) >= 30),
    ]

    return achs


ACHIEVEMENTS       = _build_achievements()
ACHIEVEMENTS_BY_ID = {a["id"]: a for a in ACHIEVEMENTS}

# Ordered display categories
CATEGORY_ORDER = [
    "Milestones", "Streaks", "Game Mastery",
    "Practice", "Exploration", "Dedication",
    "Leaderboard", "Secrets",
]
