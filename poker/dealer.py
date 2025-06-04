from typing import Sequence, Final, Collection
from . import deck, Card, Move, Rank
from .history import History
from collections import Counter


class Player:
    pass


class Dealer:
    def __init__(self, players: Sequence[Player], player_money: dict[str, int], BIG_BLIND: int):
        self.BIG_BLIND: Final = BIG_BLIND
        self.players = players                     #! remember players should be in the correct order
        self.history = History()
        self.deck = deck()
        self.active_players = {player: True for player in self.players}
        self.pot = 0
        self.player_cards: dict = {}
        self.community_cards: list = []
        self.player_money = player_money
        self.current_bet = {     
            player: (
                BIG_BLIND//2 if i == 0 else
                BIG_BLIND if i == 1 else
                0
            )
            for i, player in enumerate(self.players)
        }

    def play(self):

        for round in ('preflop', 'flop', 'turn', 'river'):
            if round == 'preflop':
                for player in self.players:
                    self.player_cards[player] = [self.deck[0], self.deck[1]] 
                    player.hand(self.deck.pop(0), self.deck.pop(0))
                self.history.last_move_amount = self.BIG_BLIND
            elif round == 'flop':
                self.community_cards.extend(self.deck[0], self.deck[1], self.deck[2])
                for player in self.players:
                    player.flop(self.deck[0], self.deck[1], self.deck[2])
                del self.deck[:3]
                self.history.last_move_amount = 0
            elif round == 'turn':
                self.community_cards.append(self.deck[0])
                for player in self.players:
                    player.turn(self.deck[0])
                del self.deck[0]
                self.history.last_move_amount = 0
            elif round == 'river':
                self.community_cards.append(self.deck[0])
                for player in self.players:
                    player.river(self.deck[0])
                del self.deck[0]
                self.history.last_move_amount = 0
            
            for player in self.players[2:]+ self.players[:2]:  # rotate players so that the player after the big blind is always first 
                if self.active_players[player]:
                    move = Move(player.decision(self.history))
                    self.history.add_move(move)
                    if move.action == 'fold':
                        self.active_players[player] = False

                        if list(self.active_players.values()).count(True) == 1:  # this means only one player is left

                            for amount in self.current_bet.values():
                                self.pot += amount
                            player.win(self.pot)         
                            return
                        
                    elif move.action == 'call':
                        if self.history.last_move_amount < self.player_money[player]:
                            self.player_money[player] -= (self.history.last_move_amount - self.current_bet[player])
                            self.current_bet[player] = self.history.last_move_amount
                            self.history.last_move_amount = self.current_bet[player]
                        else:
                            self.current_bet[player] += self.player_money[player]     #? should the player go all in, maybe there should be a warning for player.
                            self.player_money[player] = 0

                    elif move.action == 'raise':
                        raise_amount = move.amount
                        if raise_amount < self.history.last_raise:       #! remember if the last raise is not set, it will be the BIG_BLIND
                            player.handle_error("Raise amount must be same or greater than the last raise.")
                        elif raise_amount > self.player_money[player]:
                            player.handle_error("Raise amount cannot be greater than the player's money.")         #! remember to impliment more safeguards in the UI
                        else:
                            self.player_money[player] -= raise_amount
                            self.current_bet[player] += raise_amount
                            self.history.last_raise = raise_amount

            for amount in self.current_bet.values():
                self.pot += amount

            self.current_bet = {player: 0 for player in self.players}  # reset the current bet for the next round
            
        else:    # this means there will be a showdown between the remaining players

            best_hand = None

            for player in self.players:
                if self.active_players[player]:
                    if best_hand is None:
                        best_hand = self.player_cards[player] + self.community_cards
                    else: 
                        best_hand = self.showdown(best_hand, self.player_cards[player] + self.community_cards)

            winner_cards = [x for x in best_hand if x not in self.community_cards]

            winner = next(k for k, v in self.player_cards.items() if v == winner_cards)
            winner.win(self.pot)
            return

        
        
    def parse_hand(self, hand: Collection[Card]):
        RANK_ORDER = {rank: i for i, rank in enumerate(Rank, start=2)}  # mapping ranks to their order, starting from 2
        ranks = sorted((RANK_ORDER[card.rank] for card in hand), reverse=True)
        suits = [card.suit for card in hand] 
        return ranks, suits 
    
    def is_straight(self, ranks: Sequence[int]) -> bool:
        dif = 0
        for i in range(len(ranks)):
            if i !=0 and ranks[i] - ranks[i-1] != 1:
                dif += 1

        if dif == 4 or ranks == [14, 5, 4, 3, 2]:
            return True
        else:
            return False
        
    def most_common_rank(self, ranks: Collection[Card]):   

        rank_counts = Counter(ranks)
        max_rank_frequency = max(rank_counts.values())

        #find all values with that frequency
        most_common_ranks = [rank for rank, count in rank_counts.items() if count == max_rank_frequency]

        return max_rank_frequency, most_common_ranks
    

    def evaluate_hand(self, hand: Collection[Card]) -> int:
        #gives value based on hand rating, higher is better

        ranks, suits = self.parse_hand(hand)
        max_rank_frequency, most_common_ranks = self.most_common_rank(ranks)


        if len(set(suits)) == 1 and self.is_straight(ranks):
            return 8
        if max_rank_frequency == 4:
            return 7
        if (ranks.count(ranks[0]) == 3 and ranks.count(ranks[4]) == 2) or (ranks.count(ranks[0]) == 2 and ranks.count(ranks[4]) == 3):
            return 6
        if len(set(suits)) == 1:
            return 5
        if self.is_straight(ranks):
            return 4
        if max_rank_frequency == 3:
            return 3
        if max_rank_frequency == 2 and len(most_common_ranks) == 2:
            return 2
        if max_rank_frequency == 2:
            return 1
        return 0
    
    def showdown(self, hand1: Collection[Card], hand2: Collection[Card]):
        value1 = self.evaluate_hand(hand1)
        value2 = self.evaluate_hand(hand2)

        if value1 > value2:
            return hand1
        elif value2 > value1:
            return hand2
        else:
            ranks1, _ = self.parse_hand(hand1)
            ranks2, _ = self.parse_hand(hand2)
            
            if max(ranks1) > max(ranks2):
                return hand1
            elif max(ranks2) > max(ranks1):
                return hand2
            else:
                return None
