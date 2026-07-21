"""
Interactive hand simulator — play through a hand street by street.
Run with: python3 hand_sim.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bots", "mybot"))

from bot import decide

def make_state(street, your_cards, community_cards, amount_owed, pot,
               can_check, your_stack, your_bet_this_street, min_raise_to):
    return {
        "hand_id":            "sim_001",
        "street":             street,
        "seat_to_act":        3,
        "pot":                pot,
        "community_cards":    community_cards,
        "current_bet":        amount_owed,
        "min_raise_to":       min_raise_to,
        "amount_owed":        amount_owed,
        "can_check":          can_check,
        "your_cards":         your_cards,
        "your_stack":         1000,
        "your_bet_this_street": your_bet_this_street,
        "button_seat":        0,
        "last_aggressor_seat": None,
        "action_log":         [],
        "players": [
            {"seat": 0, "bot_id": "bot_a", "stack": 1000, "is_active": True, "is_folded": False, "is_all_in": False, "bet_this_street": 20},
            {"seat": 1, "bot_id": "bot_b", "stack": 1000, "is_active": True, "is_folded": False, "is_all_in": False, "bet_this_street": 10},
            {"seat": 2, "bot_id": "bot_c", "stack": 1000, "is_active": True, "is_folded": False, "is_all_in": False, "bet_this_street": 0},
            {"seat": 3, "bot_id": "mybot", "stack": your_stack, "is_active": True, "is_folded": False, "is_all_in": False, "bet_this_street": 0},
        ],
    }

def parse_cards(prompt):
    while True:
        raw = input(prompt).strip()
        if not raw:
            return []
        cards = raw.upper().replace(",", " ").split()
        normalised = []
        valid = True
        for c in cards:
            if len(c) == 2:
                normalised.append(c[0].upper() + c[1].lower())
            else:
                print(f"  Invalid card '{c}' — use format like Ah, Kd, Ts")
                valid = False
                break
        if valid:
            return normalised

def ask_action():
    print("  What does opponent do?")
    print("  1) Check  2) Bet/Raise")
    choice = input("  → ").strip()
    if choice == "2":
        amount = int(input("  How much? → ").strip())
        return amount, False
    return 0, True

def format_action(action):
    a = action.get("action")
    if a == "raise":
        return f"RAISE to {action['amount']}"
    return a.upper()

def run_sim():
    print("\n" + "="*50)
    print("  FULLHOUSE HAND SIMULATOR")
    print("="*50)

    your_cards = parse_cards("\nYour hole cards (e.g. 8d Kh): ")
    print(f"  Your hand: {' '.join(your_cards)}")

    stack = 1000
    pot   = 30
    community = []
    streets = ["preflop", "flop", "turn", "river"]
    new_cards_per_street = {"flop": 3, "turn": 1, "river": 1}

    for street in streets:
        print(f"\n── {street.upper()} " + "─"*35)
        print(f"  Pot: {pot}  |  Stack: {stack}  |  Board: {' '.join(community) if community else '(none)'}")

        if street in new_cards_per_street:
            n = new_cards_per_street[street]
            new_cards = parse_cards(f"  Enter {n} community card(s): ")
            community += new_cards
            print(f"  Board: {' '.join(community)}")

        owed, can_check = ask_action()

        state = make_state(
            street               = street,
            your_cards           = your_cards,
            community_cards      = community,
            amount_owed          = owed,
            pot                  = pot,
            can_check            = can_check,
            your_stack           = stack,
            your_bet_this_street = 0,
            min_raise_to         = max(owed * 2, 20),
        )

        action = decide(state)
        print(f"\n  Bot action: {format_action(action)}")

        a = action.get("action")
        if a == "call":
            pot   += owed
            stack -= owed
        elif a == "raise":
            amount = action["amount"]
            pot   += amount
            stack -= amount
        elif a == "fold":
            print("\n  Bot folded — hand over.")
            return

    print("\n  Hand complete.")
    print("="*50 + "\n")

if __name__ == "__main__":
    while True:
        run_sim()
        again = input("Play another hand? (y/n): ").strip().lower()
        if again != "y":
            break
