from typing import Final
from .base_player import BasePlayer
from poker import Move, Action
from poker.ml.predict import HandEvaluator
import logging

logger = logging.getLogger(__name__)


class BotPlayer(BasePlayer):
    def __init__(self, _name: str, starting_money: int, BIG_BLIND: int):
        self.money = starting_money
        self.money_given = 0
        self.BIG_BLIND: Final = BIG_BLIND
        self._name = _name
        self.hole_cards = None
        self.community_cards = []
        self.current_round_bet = 0

        try:
            self.evaluator = HandEvaluator("models/poker_model.keras")
        except Exception as e:
            logger.error(f"Failed to load hand evaluation model: {e}")
            self.evaluator = None

    @property
    def name(self) -> str:
        return self._name

    def decision(self, history) -> Move:
        """
        Decision strategy based on hand probability:
        - p < 0.3: fold (or check if no bet to call)
        - 0.3 ≤ p < 0.5: call
        - p ≥ 0.5: raise proportionally (p=1.0 goes all-in, p=0.6 raises 60% of remaining money)
        - If can't raise (insufficient funds), call instead
        """
        if self.evaluator is None or self.hole_cards is None:
            return Move(self, Action.FOLD, 0)

        try:
            hand_probability = self.evaluator.predict_hand(
                self.hole_cards, self.community_cards
            )

            if hand_probability < 0.3:
                # If there's no bet to call, check instead of folding
                if history.last_move_amount == 0:
                    logger.info(
                        f"{self.name} checking with hand probability: {hand_probability:.4f}"
                    )
                    return Move(self, Action.CALL, 0)
                logger.info(
                    f"{self.name} folding with hand probability: {hand_probability:.4f}"
                )
                return Move(self, Action.FOLD, 0)

            elif hand_probability < 0.5:
                logger.info(
                    f"{self.name} calling with hand probability: {hand_probability:.4f}"
                )
                return Move(self, Action.CALL, 0)

            else:
                raise_proportion = hand_probability
                available_money = self.money
                raise_amount = int(available_money * raise_proportion)

                if raise_amount > 0:
                    logger.info(
                        f"{self.name} raising with hand probability: {hand_probability:.4f}, raise amount: {raise_amount}"
                    )
                    return Move(self, Action.RAISE, raise_amount)
                else:
                    logger.info(
                        f"{self.name} calling with hand probability: {hand_probability:.4f}"
                    )
                    return Move(self, Action.CALL, 0)

        except Exception as e:
            logger.error(f"Error evaluating hand for {self.name}: {e}, folding")
            return Move(self, Action.FOLD, 0)

    def preflop(self, cards):
        """Store hole cards at preflop."""
        self.hole_cards = list(cards)
        self.community_cards = []
        self.current_round_bet = 0

    def flop(self, cards):
        """Update community cards on flop."""
        self.community_cards = list(cards)
        self.current_round_bet = 0

    def turn(self, card):
        """Update community cards on turn."""
        self.community_cards.append(card)
        self.current_round_bet = 0

    def river(self, card):
        """Update community cards on river."""
        self.community_cards.append(card)
        self.current_round_bet = 0

    def win(self, amount):
        self.money += amount

    def loose(self, winning_players_cards):
        """Called when the bot loses a hand."""
        logger.info(f"{self.name} lost this hand")

    def placed_bet(self, amount):
        self.money -= amount
        self.money_given += amount
        self.current_round_bet += amount
