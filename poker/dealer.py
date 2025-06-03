from typing import Sequence, Final
from . import deck, Card, Move
from .history import History


class Player:
    pass


BIG_BLIND: Final = 2


class Dealer():
    def __init__(self, players: Sequence[Player], player_money: dict[str, int]):
        self.players = players
        self.history = History()
        self.deck = deck()
        self.active_players = {player: True for player in self.players}
        self.pot = 0
        self.current_bet = {player: 0 for player in self.players}
        self.player_money = player_money

    def play(self):

        for round in ('preflop', 'flop', 'turn', 'river'):
            if round == 'preflop':
                for player in self.players:
                    player.hand(self.deck.pop(0), self.deck.pop(0))
            elif round == 'flop':
                for player in self.players:
                    player.flop(self.deck[0], self.deck[1], self.deck[2])
                del self.deck[:3]
            elif round == 'turn':
                for player in self.players:
                    player.turn(self.deck[0])
                del self.deck[0]
            elif round == 'river':
                for player in self.players:
                    player.river(self.deck[0])
                del self.deck[0]
            
            for player in self.players:
                if self.active_players[player]:
                    move = Move(player.decision(self.history))
                    self.history.add_move(player, move)
                    if move.action == 'fold':
                        self.active_players[player] = False

                        if list(self.active_players.values()).count(False) == 1:
                            return
                    elif move.action == 'call':
                        last_move_amount = self.history.last_move.amount  # ! remember to make the last move not store folds
                        if last_move_amount < self.player_money[player]:
                            self.player_money[player] -= (last_move_amount - self.current_bet[player])
                            self.current_bet[player] = last_move_amount
                        else:
                            self.current_bet[player] += self.player_money[
                                player]  # ? should the player go all in, maybe there should be a warning for player.
                            self.player_money[player] = 0

                    elif move.action == 'raise':
                        raise_amount = move.amount
                        if raise_amount < self.history.last_raise:  # ! remember if the last raise is not set, it will be the BIG_BLIND
                            pass  # TODO: handle invalid raise
                        elif raise_amount > self.player_money[player]:
                            pass  # TODO: handle invalid raise
                        else:
                            self.player_money[player] -= raise_amount
                            self.current_bet[player] += raise_amount
                            self.history.last_raise = raise_amount

            for amount in self.current_bet.values():
                self.pot += amount
                    
                            #TODO: handle end of game
