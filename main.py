from tabulate import tabulate
from os import listdir, getcwd
from binarytree import Node
from importlib import import_module
from ping_game_theory_25 import HistoryEntry, Move

CLASS_NAME: str = "Bot"

scores: dict[
    str, dict[str, int]
] = {}  # contains key as the file_name and value a dict of keys "wins","losses","points"


def match(p1: str, p2: str) -> str:
    p1_cls = getattr(import_module(p1), CLASS_NAME)
    p2_cls = getattr(import_module(p2), CLASS_NAME)

    p1_obj = p1_cls()
    p2_obj = p2_cls()

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
    print("Testing against RandomStrategy")
    start_time = time.time()
    try:
        move_self = strategy.begin()
        move_opp = opponent.begin()
    except Exception as e:
        raise AssertionError(f"begin() raised an exception: {e}")
    if not isinstance(move_self, Move):
        raise AssertionError(f"begin() returned invalid type: {type(move_self)}")
    history_self.append(HistoryEntry(self=move_self, other=move_opp))
    history_opp.append(HistoryEntry(self=move_opp, other=move_self))
    for _ in tqdm(range(self.ROUNDS - 1), desc="Running rounds"):
        if time.time() - start_time > StrategyTester.TIMEOUT_SECONDS:
            raise TimeoutError(
                f"Execution exceeded timeout of {StrategyTester.TIMEOUT_SECONDS} seconds"
            )
        try:
            move_self = strategy.turn(tuple(history_self))
        except Exception as exc:
            raise AssertionError(f"turn() raised an exception: {exc}")
        move_opp = opponent.turn(tuple(history_opp))
        if not isinstance(move_self, Move):
            raise AssertionError(f"turn() returned invalid type: {type(move_self)}")
        history_self.append(HistoryEntry(self=move_self, other=move_opp))
        history_opp.append(HistoryEntry(self=move_opp, other=move_self))
        if (
            move_self == Move.ROCK
            and move_opp == Move.SCISSOR
            or move_self == Move.PAPER
            and move_opp == Move.ROCK
            or move_self == Move.SCISSOR
            and move_opp == Move.ROCK
        ):
            self.wins += 1
        elif move_self != move_opp:
            self.losses += 1
        else:
            self.draws += 1
    total_time = time.time() - start_time
    print(f"✅ PASS: {StrategyTester.ROUNDS} rounds in {total_time:.2f} seconds")
    print(f"{self.wins} Wins, {self.losses} Losses, {self.draws} Draws")

    return p1


def update_score(res: str, p1: str, p2: str) -> None:
    if res == p1:
        scores[p1]["wins"] += 1
        scores[p1]["points"] += 3
        scores[p2]["losses"] += 1
    elif res == p2:
        scores[p2]["wins"] += 1
        scores[p2]["points"] += 3
        scores[p1]["losses"] += 1
    else:
        scores[p1]["points"] += 1
        scores[p2]["points"] += 1


def run_tournament(strategies: list[str]) -> None:
    for p1 in strategies:
        for p2 in strategies:
            if p1 == p2:
                continue

            update_score(match(p1, p2), p1, p2)

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
    (first, second, third, fourth) = list(scores.keys())[:4]

    first_r2: str = match(first, second)
    second_r2: str = match(third, fourth)
    winner: str = match(first_r2, second_r2)

    root = Node(winner)
    root.left = Node(first_r2)
    root.right = Node(second_r2)
    root.left.left = Node(first)
    root.left.right = Node(second)
    root.right.left = Node(third)
    root.right.right = Node(fourth)

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
