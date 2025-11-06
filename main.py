from tabulate import tabulate
from os import listdir, getcwd
from binarytree import Node

scores: dict[
    str, dict[str, int]
] = {}  # contains key as the file_name and value a dict of keys "wins","losses","points"


def match(p1: str, p2: str) -> str:
    return p1


def update_score(res: str, p1: str, p2: str):
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


def run_tournament(strategies: list[str]):
    for p1 in strategies:
        for p2 in strategies:
            if p1 == p2:
                continue

            update_score(match(p1, p2), p1, p2)

    scoreboard = []
    k = 0
    for item in scores.items():
        scoreboard.append([])
        scoreboard[k].append(item[0])
        scoreboard[k].append(item[1]["wins"])
        scoreboard[k].append(item[1]["losses"])
        scoreboard[k].append(item[1]["points"])
        k += 1

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
    #


def run_playoffs():
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
        net_id = submission.strip().lower().split("_")[1].split(".")[0]
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
