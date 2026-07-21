"""
Run this on your Mac to generate the preflop equity lookup table.
cd ~/Documents/fullhouse-engine
python3 build_equity_table.py
"""
import eval7
import random

RANKS = "23456789TJQKA"

def compute_equity(rank1, rank2, suited, trials=10000):
    if suited:
        hole = [eval7.Card(rank1 + "s"), eval7.Card(rank2 + "s")]
    else:
        hole = [eval7.Card(rank1 + "s"), eval7.Card(rank2 + "h")]

    deck = eval7.Deck()
    deck.cards = [c for c in deck.cards if c not in hole]

    wins = ties = 0
    for _ in range(trials):
        deck.shuffle()
        opp   = deck.cards[:2]
        board = deck.cards[2:7]
        our   = eval7.evaluate(hole + board)
        opp_s = eval7.evaluate(opp + board)
        if our > opp_s:   wins += 1
        elif our == opp_s: ties += 1
    return round((wins + ties * 0.5) / trials, 4)

rank_list = list(reversed(RANKS))
equity_table = {}
total = 0

for i, r1 in enumerate(rank_list):
    for j, r2 in enumerate(rank_list):
        if i > j:
            continue
        if i == j:
            key = r1 + r2
            eq  = compute_equity(r1, r2, False)
            equity_table[key] = eq
            total += 1
            print(f"  {key}: {eq}  ({total}/169)")
        else:
            key_s = r1 + r2 + "s"
            key_o = r1 + r2 + "o"
            eq_s  = compute_equity(r1, r2, True)
            eq_o  = compute_equity(r1, r2, False)
            equity_table[key_s] = eq_s
            equity_table[key_o] = eq_o
            total += 2
            print(f"  {key_s}: {eq_s}  {key_o}: {eq_o}  ({total}/169)")

print("\n\nPREFLOP_EQUITY = {")
for k, v in sorted(equity_table.items()):
    print(f'    "{k}": {v},')
print("}")
