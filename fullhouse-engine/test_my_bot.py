import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.game import PokerEngine, STARTING_STACK, BIG_BLIND, SMALL_BLIND
import importlib.util

def load_bot(path):
    spec = importlib.util.spec_from_file_location("bot", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

my_bot        = load_bot("bots/mybot/bot.py")
aggressor     = load_bot("bots/aggressor/bot.py")
mathematician = load_bot("bots/mathematician/bot.py")
shark         = load_bot("bots/shark/bot.py")
template      = load_bot("bots/template/bot.py")

BOT_MAP = {
    "mybot":         my_bot,
    "aggressor":     aggressor,
    "mathematician": mathematician,
    "shark":         shark,
    "template":      template,
}

def run_match(bot_ids, hands=400, verbose=False):
    eng = PokerEngine("match", bot_ids, dealer_seat=0)
    stacks = {bid: STARTING_STACK for bid in bot_ids}
    for hand_num in range(hands):
        if hand_num % 50 == 0:
            print("  Hand " + str(hand_num) + "/" + str(hands) + "...", flush=True)
        state = eng.start_hand()
        while state.get("type") == "action_request":
            seat    = state["seat_to_act"]
            bot_id  = bot_ids[seat]
            bot_mod = BOT_MAP[bot_id]
            try:
                action = bot_mod.decide(state)
            except Exception as e:
                print("  python3 test_my_bot.py " + bot_id + " crashed: " + str(e))
                action = {"action": "fold"}
            state = eng.apply_action(seat, action)
        stacks = state["final_stacks"]
        if any(s <= 0 for s in stacks.values()):
            break
    return stacks

def print_result(label, bot_ids, result):
    print("")
    print("-- " + label)
    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    for i, (bot_id, stack) in enumerate(sorted_result):
        marker = " <- you" if bot_id == "mybot" else ""
        print("  " + str(i+1) + ". " + bot_id.ljust(15) + str(stack).rjust(6) + " chips" + marker)
    my_stack = result.get("mybot", 0)
    others   = [v for k, v in result.items() if k != "mybot"]
    avg_opp  = sum(others) / max(len(others), 1)
    print("  WINNING vs field average" if my_stack > avg_opp else "  LOSING vs field average")

def test_vs_aggressor():
    result = run_match(["mybot", "aggressor"], hands=400)
    print_result("My bot vs Aggressor (400 hands)", ["mybot", "aggressor"], result)

def test_vs_mathematician():
    result = run_match(["mybot", "mathematician"], hands=400)
    print_result("My bot vs Mathematician (400 hands)", ["mybot", "mathematician"], result)

def test_vs_shark():
    result = run_match(["mybot", "shark"], hands=400)
    print_result("My bot vs Shark (400 hands)", ["mybot", "shark"], result)

def test_vs_all():
    ids    = ["mybot", "template", "aggressor", "mathematician", "shark", "shark"]
    result = run_match(ids, hands=400)
    print_result("6-player table vs all bots (400 hands)", ids, result)

def test_chip_conservation():
    print("")
    print("-- Chip conservation")
    ids    = ["mybot", "aggressor", "shark"]
    result = run_match(ids, hands=100)
    total  = sum(result.values())
    expected = STARTING_STACK * len(ids)
    ok = abs(total - expected) < 10
    print("  Total: " + str(total) + " expected " + str(expected))
    print("  OK" if ok else "  CHIP LEAK DETECTED")

if __name__ == "__main__":
    tests = [test_vs_aggressor, test_vs_mathematician, test_vs_shark, test_vs_all, test_chip_conservation]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print("FAILED " + t.__name__ + ": " + str(e))
            import traceback
            traceback.print_exc()
            failed += 1
    print("")
    print("Results: " + str(passed) + " passed, " + str(failed) + " failed")