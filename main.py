from tabulate import tabulate
from os import listdir, getcwd
from binarytree import Node
from importlib import import_module
from ping_game_theory import HistoryEntry, Move
from time import time
from typing import Final
from random import seed

CLASS_NAME: str = "Bot"

scores: dict[
    str, dict[str, int]
] = {}  # contains key as the file_name and value a dict of keys "wins","losses","points"


ROUNDS: Final[int] = 10_000
PAYOFFS: Final[dict] = {
    Move.COOPERATE: {
        Move.COOPERATE: (3, 3),  # Mutual cooperation
        Move.DEFECT: (0, 5),  # Sucker's payoff
    },
    Move.DEFECT: {
        Move.COOPERATE: (5, 0),  # Temptation to defect
        Move.DEFECT: (1, 1),  # Mutual defection
    },
}


def match(p1: str, p2: str) -> tuple[str, int, int]:
    print(f"{p1} vs {p2}")

    p1_cls = getattr(import_module(p1), CLASS_NAME)
    p2_cls = getattr(import_module(p2), CLASS_NAME)
    total_score_self: int = 0
    total_score_opp: int = 0

    try:
        strategy = p1_cls()
    except Exception as e:
        raise AssertionError(f"Strategy failed to initialize: {e}")
    try:
        opponent = p2_cls()
    except Exception as e:
        raise AssertionError(f"Strategy failed to initialize: {e}")

    history_self: list[HistoryEntry] = []
    history_opp: list[HistoryEntry] = []

    print(f"{strategy.strategy_name} vs {opponent.strategy_name}")

    start_time = time()
    try:
        move_self = strategy.begin()
        move_opp = opponent.begin()
    except Exception as e:
        raise AssertionError(f"begin() raised an exception: {e}")
    if not isinstance(move_self, Move):
        raise AssertionError(f"begin() returned invalid type: {type(move_self)}")
    # Record first round
    history_self.append(HistoryEntry(self=move_self, other=move_opp))
    history_opp.append(HistoryEntry(self=move_opp, other=move_self))
    # Calculate payoffs for first round
    payoff_self, payoff_opp = PAYOFFS[move_self][move_opp]
    total_score_self += payoff_self
    total_score_opp += payoff_opp
    for _ in tqdm(range(ROUNDS - 1), desc="Running rounds"):
        try:
            move_self = strategy.turn(tuple(history_self))
        except Exception as exc:
            raise AssertionError(f"turn() raised an exception: {exc}")
        move_opp = opponent.turn(tuple(history_opp))
        if not isinstance(move_self, Move):
            raise AssertionError(f"turn() returned invalid type: {type(move_self)}")
        # Record moves
        history_self.append(HistoryEntry(self=move_self, other=move_opp))
        history_opp.append(HistoryEntry(self=move_opp, other=move_self))
        payoff_self, payoff_opp = PAYOFFS[move_self][move_opp]
        total_score_self += payoff_self
        total_score_opp += payoff_opp
        seed(None)
    total_time = time() - start_time
    avg_score_self = total_score_self / ROUNDS
    avg_score_opp = total_score_opp / ROUNDS
    print(f"✅ PASS: {ROUNDS} rounds in {total_time:.2f} seconds")
    print(f"Strategy Total Score: {total_score_self} (avg: {avg_score_self:.2f})")
    print(f"Opponent Total Score: {total_score_opp} (avg: {avg_score_opp:.2f})")

    # Draw
    if abs(total_score_self - total_score_opp) <= 5:
        return ("", total_score_self, total_score_opp)

    if total_score_self > total_score_opp:
        winner = p1
    else:
        winner = p2

    return (winner, total_score_self, total_score_opp)


def run_tournament(strategies: list[str]) -> None:
    for p1 in strategies:
        for p2 in strategies:
            if p1 == p2:
                continue

            try:
                res = match(p1, p2)
            except Exception as e:
                print(f"Exception raised: -\n{e}")

            if res[0] == p1:
                scores[p1]["wins"] += 1
            elif res[0] == p2:
                scores[p2]["wins"] += 1

            scores[p1]["points"] += res[1]
            scores[p2]["points"] += res[2]

    scoreboard = []
    i = 0
    for item in scores.items():
        scoreboard.append([])
        scoreboard[i].append(item[0])
        scoreboard[i].append(item[1]["wins"])
        scoreboard[i].append(item[1]["losses"])
        scoreboard[i].append(item[1]["points"])
        i += 1

    print(
        tabulate(
            scoreboard,
            headers=["Contestant", "Wins", "Losses", "Points"],
            tablefmt="grid",
        )
    )

    # with open("ping_hack_25_results.txt", "w") as f:
    #     f.write(to_save)
    #     f.write("\n")
    #     f.write("-" * 30)


def run_playoffs() -> None:
    (first, second, third, fourth) = map(
        lambda fname: fname.split("_")[0], list(scores.keys())[:4]
    )

    try:
        q1 = match(first, second)[0]
    except Exception as e:
        print(f"Exception raised: -\n{e}")

    if q1 == first:
        loser = second
    else:
        loser = first

    try:
        eliminator = match(third, fourth)[0]
        q2 = match(loser, eliminator)[0]
        final = match(q1, q2)[0]
    except Exception as e:
        print(f"Exception raised: -\n{e}")

    root = Node(final)
    root.left = Node(q1)
    root.left.left = first
    root.left.right = second
    root.right = Node(q2)
    root.right.left = loser
    root.right.right = Node(eliminator)
    root.right.right.left = third
    root.right.right.right = fourth

    print(root)


if __name__ == "__main__":
    # Load strategies' data

    strategies: list[str] = []  # contains the name of each file
    submission_files: list[str] = list(
        filter(lambda fname: fname[-2:] == "py", listdir(getcwd()))
    )
    for submission in submission_files:
        net_id = submission.strip().lower()
        strategies.append(net_id)
        scores[net_id] = {"wins": 0, "losses": 0, "points": 0}

    print("Tournament Round 1\n")
    run_tournament(strategies)
    print("Tournament Round 2\n")
    run_tournament(strategies)

    scores = dict(
        sorted(scores.items(), key=lambda item: item[1]["points"], reverse=True)
    )

    print("Playoffs: -\n")
    run_playoffs()
