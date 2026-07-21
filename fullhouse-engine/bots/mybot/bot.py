"""
James Murphy.
"""
import random
from collections import Counter
from itertools import combinations


BET_SIZES = {"thin": 0.4, "normal": 0.6, "strong": 0.8}

opponent_stats = {}

try:
    import eval7
    USE_EVAL7 = True
except ImportError:
    USE_EVAL7 = False

EVAL7_THRESHOLDS = {
    "monster": 100_000_000,
    "strong":   34_000_000,
    "medium":   17_000_000,
}

RANK_ORDER = "23456789TJQKA"
RANK_VALUE  = {r: i for i, r in enumerate(RANK_ORDER)}

# ── Precomputed preflop equity table (10,000 trial Monte Carlo, computed offline)
# Instant O(1) lookup — replaces runtime Monte Carlo entirely
PREFLOP_EQUITY = {
    "22": 0.503,
    "32o": 0.3192,
    "32s": 0.3578,
    "33": 0.5334,
    "42o": 0.3374,
    "42s": 0.372,
    "43o": 0.35,
    "43s": 0.3967,
    "44": 0.5645,
    "52o": 0.334,
    "52s": 0.3801,
    "53o": 0.3644,
    "53s": 0.4008,
    "54o": 0.3862,
    "54s": 0.4121,
    "55": 0.6089,
    "62o": 0.3409,
    "62s": 0.3796,
    "63o": 0.3602,
    "63s": 0.4021,
    "64o": 0.3868,
    "64s": 0.4091,
    "65o": 0.3986,
    "65s": 0.4371,
    "66": 0.6399,
    "72o": 0.3528,
    "72s": 0.3826,
    "73o": 0.3695,
    "73s": 0.3991,
    "74o": 0.3805,
    "74s": 0.4195,
    "75o": 0.4067,
    "75s": 0.4354,
    "76o": 0.4174,
    "76s": 0.4426,
    "77": 0.6617,
    "82o": 0.3679,
    "82s": 0.3972,
    "83o": 0.3808,
    "83s": 0.4189,
    "84o": 0.3972,
    "84s": 0.4291,
    "85o": 0.4157,
    "85s": 0.447,
    "86o": 0.4335,
    "86s": 0.457,
    "87o": 0.4507,
    "87s": 0.4788,
    "88": 0.6853,
    "92o": 0.3886,
    "92s": 0.4254,
    "93o": 0.4025,
    "93s": 0.4261,
    "94o": 0.4001,
    "94s": 0.4422,
    "95o": 0.4238,
    "95s": 0.4602,
    "96o": 0.441,
    "96s": 0.4713,
    "97o": 0.4616,
    "97s": 0.4921,
    "98o": 0.4746,
    "98s": 0.5012,
    "99": 0.7254,
    "A2o": 0.5476,
    "A2s": 0.5596,
    "A3o": 0.5607,
    "A3s": 0.5895,
    "A4o": 0.5693,
    "A4s": 0.5901,
    "A5o": 0.5733,
    "A5s": 0.596,
    "A6o": 0.5767,
    "A6s": 0.5926,
    "A7o": 0.5885,
    "A7s": 0.6156,
    "A8o": 0.6047,
    "A8s": 0.6221,
    "A9o": 0.6024,
    "A9s": 0.6329,
    "AA": 0.8565,
    "AJo": 0.638,
    "AJs": 0.6489,
    "AKo": 0.6479,
    "AKs": 0.6661,
    "AQo": 0.6365,
    "AQs": 0.6599,
    "ATo": 0.62,
    "ATs": 0.6449,
    "J2o": 0.4407,
    "J2s": 0.4778,
    "J3o": 0.4572,
    "J3s": 0.4876,
    "J4o": 0.4652,
    "J4s": 0.4904,
    "J5o": 0.4744,
    "J5s": 0.4965,
    "J6o": 0.4793,
    "J6s": 0.5037,
    "J7o": 0.4888,
    "J7s": 0.5188,
    "J8o": 0.524,
    "J8s": 0.5356,
    "J9o": 0.5362,
    "J9s": 0.5457,
    "JJ": 0.7724,
    "JTo": 0.5474,
    "JTs": 0.5711,
    "K2o": 0.4985,
    "K2s": 0.5351,
    "K3o": 0.5219,
    "K3s": 0.5458,
    "K4o": 0.5244,
    "K4s": 0.5509,
    "K5o": 0.5357,
    "K5s": 0.5629,
    "K6o": 0.5442,
    "K6s": 0.5663,
    "K7o": 0.553,
    "K7s": 0.5758,
    "K8o": 0.5538,
    "K8s": 0.5725,
    "K9o": 0.5811,
    "K9s": 0.6017,
    "KJo": 0.6152,
    "KJs": 0.6252,
    "KK": 0.8253,
    "KQo": 0.6051,
    "KQs": 0.6284,
    "KTo": 0.5941,
    "KTs": 0.621,
    "Q2o": 0.4733,
    "Q2s": 0.5018,
    "Q3o": 0.483,
    "Q3s": 0.5188,
    "Q4o": 0.493,
    "Q4s": 0.5115,
    "Q5o": 0.5045,
    "Q5s": 0.5299,
    "Q6o": 0.5167,
    "Q6s": 0.5377,
    "Q7o": 0.513,
    "Q7s": 0.5446,
    "Q8o": 0.5263,
    "Q8s": 0.5552,
    "Q9o": 0.5504,
    "Q9s": 0.5702,
    "QJo": 0.5807,
    "QJs": 0.5978,
    "QQ": 0.7944,
    "QTo": 0.5654,
    "QTs": 0.5972,
    "T2o": 0.414,
    "T2s": 0.4428,
    "T3o": 0.422,
    "T3s": 0.4512,
    "T4o": 0.4293,
    "T4s": 0.4606,
    "T5o": 0.448,
    "T5s": 0.4737,
    "T6o": 0.4607,
    "T6s": 0.4848,
    "T7o": 0.4872,
    "T7s": 0.5054,
    "T8o": 0.4835,
    "T8s": 0.524,
    "T9o": 0.5183,
    "T9s": 0.5427,
    "TT": 0.7529,
}

def preflop_equity(hole_cards):
    """Instant O(1) lookup — no Monte Carlo, no timeout risk."""
    try:
        r1 = hole_cards[0][0].upper()
        r2 = hole_cards[1][0].upper()
        s1 = hole_cards[0][1].lower()
        s2 = hole_cards[1][1].lower()
        suited = s1 == s2

        # Sort ranks high to low
        if RANK_VALUE[r1] < RANK_VALUE[r2]:
            r1, r2 = r2, r1

        if r1 == r2:
            key = r1 + r2
        elif suited:
            key = r1 + r2 + "s"
        else:
            key = r1 + r2 + "o"

        return PREFLOP_EQUITY.get(key, 0.5)
    except Exception:
        return 0.5

# ── Stdlib hand evaluation ────────────────────────────────────────────────────

def _score_five(cards):
    ranks = sorted([RANK_VALUE[c[0].upper()] for c in cards], reverse=True)
    suits = [c[1].lower() for c in cards]
    counts = sorted(Counter(ranks).values(), reverse=True)
    flush    = len(set(suits)) == 1
    straight = len(set(ranks)) == 5 and ranks[0] - ranks[4] == 4
    if set(ranks) == {12, 0, 1, 2, 3}:
        straight, ranks = True, [3, 2, 1, 0, -1]
    if straight and flush:     return (8, ranks)
    if counts == [4, 1]:       return (7, ranks)
    if counts == [3, 2]:       return (6, ranks)
    if flush:                  return (5, ranks)
    if straight:               return (4, ranks)
    if counts == [3, 1, 1]:    return (3, ranks)
    if counts == [2, 2, 1]:    return (2, ranks)
    if counts == [2, 1, 1, 1]: return (1, ranks)
    return (0, ranks)

def _evaluate_stdlib(cards):
    best = None
    for five in combinations(cards, 5):
        score = _score_five(five)
        if best is None or score > best:
            best = score
    return best

def _hand_category_stdlib(score):
    cat = score[0]
    if cat >= 6: return "monster"
    if cat >= 3: return "strong"
    if cat >= 1: return "medium"
    return "weak"

def postflop_strength(hole_cards, community_cards):
    try:
        if USE_EVAL7:
            all_cards = [eval7.Card(c) for c in hole_cards + community_cards]
            score = eval7.evaluate(all_cards)
            if score >= EVAL7_THRESHOLDS["monster"]: return "monster"
            if score >= EVAL7_THRESHOLDS["strong"]:  return "strong"
            if score >= EVAL7_THRESHOLDS["medium"]:  return "medium"
            return "weak"
        else:
            score = _evaluate_stdlib(hole_cards + community_cards)
            return _hand_category_stdlib(score)
    except Exception:
        return "medium"

# ── Opponent modelling ────────────────────────────────────────────────────────

def update_stats(bot_id, action):
    if bot_id not in opponent_stats:
        opponent_stats[bot_id] = {
            "folds": 0, "raises": 0, "calls": 0, "hands": 0
        }
    s = opponent_stats[bot_id]
    if action == "fold":  s["folds"] += 1
    if action == "raise": s["raises"] += 1
    if action == "call":  s["calls"] += 1
    s["hands"] += 1

def get_fold_freq(bot_id):
    s = opponent_stats.get(bot_id, {})
    hands = s.get("hands", 0)
    if hands < 4:
        return 0.5
    return s["folds"] / hands

def get_aggression(bot_id):
    s = opponent_stats.get(bot_id, {})
    actions = s.get("calls", 0) + s.get("raises", 0)
    if actions < 4:
        return 0.5
    return s.get("raises", 0) / max(actions, 1)

def parse_action_log(action_log, my_seat):
    for entry in action_log:
        seat   = entry.get("seat")
        bot_id = entry.get("bot_id")
        action = entry.get("action")
        if seat is not None and seat != my_seat and action and bot_id:
            update_stats(bot_id, action)

# ── Stack standing ────────────────────────────────────────────────────────────

def relative_standing(gs):
    my_stack   = gs["your_stack"]
    all_stacks = [p["stack"] for p in gs["players"] if not p["is_folded"] and not p["is_all_in"]]
    avg        = sum(all_stacks) / max(len(all_stacks), 1)
    if my_stack > avg * 1.3: return "leading"
    if my_stack < avg * 0.6: return "short_stack"
    return "middle"

# ── Draw detection ────────────────────────────────────────────────────────────

def draw_strength(hole_cards, community_cards, street):
    if street == "river":
        return None
    all_cards  = hole_cards + community_cards
    suits      = [c[1].lower() for c in all_cards]
    hole_suits = [c[1].lower() for c in hole_cards]
    hole_ranks = [RANK_VALUE[c[0].upper()] for c in hole_cards]
    suit_counts = Counter(suits)
    for suit, count in suit_counts.items():
        if count >= 4 and suit in hole_suits:
            return "flush_draw"
    all_ranks = sorted(set([RANK_VALUE[c[0].upper()] for c in all_cards]))
    for low in range(0, 10):
        window = set(range(low, low + 5))
        hits   = window & set(all_ranks)
        hole_in_window = any(r in window for r in hole_ranks)
        if not hole_in_window:
            continue
        if len(hits) == 4:
            missing = window - hits
            gap_pos = list(missing)[0]
            if gap_pos == low or gap_pos == low + 4:
                return "oesd"
            else:
                return "gutshot"
    return None

# ── Preflop ───────────────────────────────────────────────────────────────────

def decide_preflop(gs, position, fold_freq, aggression, standing):
    total_hands = sum(s.get("hands", 0) for s in opponent_stats.values())
    early_game  = total_hands < 15
    owed  = gs["amount_owed"]
    pot   = gs["pot"]
    stack = gs["your_stack"]

    equity = preflop_equity(gs["your_cards"])

    if equity >= 0.65:
        multiplier = 4 if equity >= 0.75 else 3
        if standing == "leading":
            multiplier += 1
        raise_to = min(gs["min_raise_to"] * multiplier, stack)
        return {"action": "raise", "amount": raise_to}

    call_threshold = 0.58 if early_game else 0.52
    if equity >= call_threshold:
        if position > 0.5:
            if fold_freq > 0.55 and owed < pot * 0.3:
                raise_to = min(gs["min_raise_to"] * 2, stack)
                return {"action": "raise", "amount": raise_to}
            if owed < pot * 0.3:
                return {"action": "call"}
        else:
            if owed < pot * 0.12:
                return {"action": "call"}

    spec_threshold = 0.52 if early_game else 0.46
    if equity >= spec_threshold and position > 0.7 and owed < pot * 0.08:
        return {"action": "call"}

    if gs["amount_owed"] < stack * 0.07 and equity >= 0.40:
        return {"action": "call"}

    if gs["can_check"]:
        return {"action": "check"}
    return {"action": "fold"}

# ── Postflop ──────────────────────────────────────────────────────────────────

def decide_postflop(gs, position, fold_freq, aggression, standing):
    owed  = gs["amount_owed"]
    pot   = gs["pot"]
    stack = gs["your_stack"]
    street = gs["street"]
    made_hand = postflop_strength(gs["your_cards"], gs.get("community_cards", []))

    if gs["can_check"]:
        if made_hand == "monster":
            if aggression > 0.6 and random.random() < 0.3:
                return {"action": "check"}
            bet = min(int(pot * BET_SIZES["strong"]), stack)
            bet = max(bet, gs["min_raise_to"])
            return {"action": "raise", "amount": bet}

        if made_hand == "strong":
            bet = min(int(pot * BET_SIZES["normal"]), stack)
            bet = max(bet, gs["min_raise_to"])
            return {"action": "raise", "amount": bet}

        if position > 0.6:
            draw = draw_strength(gs["your_cards"], gs.get("community_cards", []), street)
            if draw == "flush_draw":
                base_freq = 0.7
            elif draw == "oesd":
                base_freq = 0.6
            elif draw == "gutshot":
                base_freq = 0.3
            else:
                base_freq = 0.55 if fold_freq > 0.55 else 0.2
            if standing == "leading":     base_freq = min(base_freq + 0.15, 0.8)
            if standing == "short_stack": base_freq = max(base_freq - 0.15, 0.05)
            if random.random() < base_freq:
                bet = min(int(pot * BET_SIZES["thin"]), stack)
                bet = max(bet, gs["min_raise_to"])
                return {"action": "raise", "amount": bet}

        return {"action": "check"}

    pot_odds = owed / max(pot, 1)

    if made_hand == "monster":
        if pot_odds <= 0.8:
            raise_to = min(int(pot * 1.2), stack)
            raise_to = max(raise_to, gs["min_raise_to"])
            return {"action": "raise", "amount": raise_to}
        return {"action": "call"}

    if made_hand == "strong":
        if pot_odds <= 0.6:
            raise_to = min(int(pot * 0.9), stack)
            raise_to = max(raise_to, gs["min_raise_to"])
            return {"action": "raise", "amount": raise_to}
        if pot_odds <= 0.75:
            return {"action": "call"}

    if made_hand == "medium":
        board_ranks  = [c[0].upper() for c in gs.get("community_cards", [])]
        hole_ranks   = [c[0].upper() for c in gs["your_cards"]]
        top_board    = max(board_ranks, key=lambda r: RANK_VALUE[r]) if board_ranks else None
        has_top_pair = top_board and top_board in hole_ranks
        if has_top_pair:
            threshold = 0.65 if position > 0.5 else 0.45
        else:
            threshold = 0.6 if position > 0.5 else 0.45
        if pot_odds <= threshold:
            return {"action": "call"}

    if made_hand == "weak":
        draw = draw_strength(gs["your_cards"], gs.get("community_cards", []), street)
        if draw == "flush_draw":
            if pot_odds <= 0.4:
                return {"action": "call"}
            if pot_odds <= 0.6 and position > 0.5:
                raise_to = min(int(pot * 0.7), stack)
                raise_to = max(raise_to, gs["min_raise_to"])
                return {"action": "raise", "amount": raise_to}
        if draw == "oesd":
            if pot_odds <= 0.35:
                return {"action": "call"}
        if draw == "gutshot":
            if pot_odds <= 0.15:
                return {"action": "call"}
        if pot_odds <= 0.08 and fold_freq < 0.4:
            return {"action": "call"}

    if gs["amount_owed"] < stack * 0.07:
        made = postflop_strength(gs["your_cards"], gs.get("community_cards", []))
        if made in ("monster", "strong") or gs["amount_owed"] < stack * 0.03:
            return {"action": "call"}

    return {"action": "fold"}

# ── Entry point ───────────────────────────────────────────────────────────────

def decide(game_state: dict) -> dict:
    seat = game_state["seat_to_act"]
    n    = len(game_state["players"])
    button   = game_state.get("button_seat", 0)
    position = ((seat - button) % n) / max(n - 1, 1)

    parse_action_log(game_state.get("action_log", []), seat)

    opponents = [p for p in game_state["players"] if p["seat"] != seat]
    fold_freqs  = []
    aggressions = []
    for p in opponents:
        bid = p.get("bot_id")
        if bid:
            fold_freqs.append(get_fold_freq(bid))
            aggressions.append(get_aggression(bid))

    fold_freq  = sum(fold_freqs)  / len(fold_freqs)  if fold_freqs  else 0.5
    aggression = sum(aggressions) / len(aggressions) if aggressions else 0.5
    standing   = relative_standing(game_state)

    if game_state["street"] == "preflop":
        return decide_preflop(game_state, position, fold_freq, aggression, standing)
    else:
        return decide_postflop(game_state, position, fold_freq, aggression, standing)
    