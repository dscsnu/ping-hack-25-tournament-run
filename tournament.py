import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Type, List, Tuple
from tqdm import tqdm


class Move(StrEnum):
    COOPERATE = "COOPERATE"
    DEFECT = "DEFECT"


@dataclass
class HistoryEntry:
    self: Move
    other: Move


History = Tuple[HistoryEntry, ...]


class Strategy(ABC):
    @abstractmethod
    def begin(self) -> Move:
        """Return the first move of the strategy."""
        ...

    @abstractmethod
    def turn(self, history: History) -> Move:
        """Return the next move based on the game history."""
        ...


class RandomStrategy(Strategy):
    def __init__(self) -> None:
        self.author_netid = ""
        self.strategy_name = ""
        self.strategy_description = ""

    def begin(self) -> Move:
        return random.choice(list(Move))

    def turn(self, history: History) -> Move:
        return self.begin()


class StrategyTester:
    ROUNDS: Final[int] = 999
    TIMEOUT_SECONDS: Final[int] = 60

    # Payoff matrix: (self_payoff, other_payoff)
    # Format: PAYOFFS[self_move][other_move]
    PAYOFFS: Final[dict] = {
        Move.COOPERATE: {
            Move.COOPERATE: (3, 3),
            Move.DEFECT: (0, 5),
        },
        Move.DEFECT: {
            Move.COOPERATE: (5, 0),
            Move.DEFECT: (1, 1),
        },
    }

    def __init__(self, strategy_cls: Type[Strategy]) -> None:
        self.total_score_self: int = 0
        self.total_score_opp: int = 0
        self.strategy_cls = strategy_cls

    def run(self) -> None:
        try:
            strategy = self.strategy_cls()
        except Exception as e:
            raise AssertionError(f"Strategy failed to initialize: {e}")

        opponent = RandomStrategy()
        history_self: List[HistoryEntry] = []
        history_opp: List[HistoryEntry] = []

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

        payoff_self, payoff_opp = self.PAYOFFS[move_self][move_opp]
        self.total_score_self += payoff_self
        self.total_score_opp += payoff_opp

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

            payoff_self, payoff_opp = self.PAYOFFS[move_self][move_opp]
            self.total_score_self += payoff_self
            self.total_score_opp += payoff_opp

        total_time = time.time() - start_time
        avg_score_self = self.total_score_self / self.ROUNDS
        avg_score_opp = self.total_score_opp / self.ROUNDS

        print(f"✅ PASS: {StrategyTester.ROUNDS} rounds in {total_time:.2f} seconds")
        print(
            f"Strategy Total Score: {self.total_score_self} (avg: {avg_score_self:.2f})"
        )
        print(
            f"Opponent Total Score: {self.total_score_opp} (avg: {avg_score_opp:.2f})"
        )


__all__ = ["History", "HistoryEntry", "Move", "Strategy", "StrategyTester"]
