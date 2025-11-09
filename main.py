import sys
from pathlib import Path

from binarytree import Node
from tabulate import tabulate
import matplotlib.pyplot as plt
from importlib import import_module
from ping_game_theory import HistoryEntry, Move
from time import time
from typing import Final
from random import seed
from tqdm import tqdm

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


def resolve_draw(p1: str, p2: str) -> str:
    data_p1 = scores.get(p1)
    data_p2 = scores.get(p2)

    if data_p1 is None or data_p2 is None:
        raise RuntimeError(
            "Cannot resolve draw because one or both strategies are missing from "
            f"the scoreboard: {p1}, {p2}."
        )

    points_p1 = data_p1["points"]
    points_p2 = data_p2["points"]
    if points_p1 != points_p2:
        return p1 if points_p1 > points_p2 else p2

    wins_p1 = data_p1["wins"]
    wins_p2 = data_p2["wins"]
    if wins_p1 != wins_p2:
        return p1 if wins_p1 > wins_p2 else p2

    # Final fallback: alphabetical order for deterministic choice.
    return min(p1, p2)


def run_tournament(strategies: list[str]) -> list[list[int | str]]:
    for p1 in strategies:
        for p2 in strategies:
            if p1 == p2:
                continue
            try:
                res = match(p1, p2)
            except Exception as e:
                print(f"Exception raised while matching {p1} vs {p2}:\n{e}")
                raise

            if res[0] == p1:
                scores[p1]["wins"] += 1
            elif res[0] == p2:
                scores[p2]["wins"] += 1

            scores[p1]["points"] += res[1]
            scores[p2]["points"] += res[2]

    sorted_scores = sorted(
        scores.items(), key=lambda item: item[1]["points"], reverse=True
    )
    scoreboard = [
        [rank, name, data["wins"], data["points"]]
        for rank, (name, data) in enumerate(sorted_scores, start=1)
    ]

    print(
        tabulate(
            scoreboard,
            headers=["Rank", "Contestant", "Wins", "Points"],
            tablefmt="grid",
        )
    )

    return scoreboard


def generate_round_graph(scoreboard: list[list[int | str]], round_label: str) -> None:
    contestants = [row[1] for row in scoreboard]
    points = [row[3] for row in scoreboard]

    if not contestants:
        print(f"No data available to plot for {round_label}.")
        return

    width = max(8.0, len(contestants) * 0.6)
    plt.figure(figsize=(width, 6))
    bars = plt.bar(contestants, points, color="#4C72B0")
    plt.xlabel("Contestant")
    plt.ylabel("Points")
    plt.title(f"Tournament {round_label} Points")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    for bar, point in zip(bars, points):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(point),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    output_path = (
        Path.cwd()
        / f"tournament_{round_label.replace(' ', '_').lower()}_points.png"
    )
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved {round_label} points chart to {output_path}")

    # with open("ping_hack_25_results.txt", "w") as f:
    #     f.write(to_save)
    #     f.write("\n")
    #     f.write("-" * 30)


if __name__ == "__main__":
    # Load strategies' data

    strategies: list[str] = []  # contains the name of each file
    submissions_dir = Path.cwd() / "submissions"

    if not submissions_dir.exists():
        raise FileNotFoundError(f"Expected submissions directory at {submissions_dir}")

    if str(submissions_dir) not in sys.path:
        sys.path.insert(0, str(submissions_dir))

    submission_files = sorted(
        (
            path
            for path in submissions_dir.iterdir()
            if path.suffix == ".py" and path.name != "__init__.py"
        ),
        key=lambda path: path.name.lower(),
    )

    if not submission_files:
        raise RuntimeError(f"No Python submissions found in {submissions_dir}")

    for submission_path in submission_files:
        module_name = submission_path.stem
        strategies.append(module_name)
        scores[module_name] = {"wins": 0, "losses": 0, "points": 0}

    print("Tournament Round 1\n")
    round1_scoreboard = run_tournament(strategies)
    generate_round_graph(round1_scoreboard, "Round 1")

    print("Final Round\n")
    round2_scoreboard = run_tournament(strategies)
    generate_round_graph(round2_scoreboard, "Final Round")

    scores = dict(
        sorted(scores.items(), key=lambda item: item[1]["points"], reverse=True)
    )
