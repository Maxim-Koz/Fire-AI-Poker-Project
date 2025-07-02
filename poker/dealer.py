from typing import Sequence, Final, Collection, List, Tuple
from . import deck, Card, Rank, Action, Suit
from .history import History
from .poker_logic import showdown
from .players.base_player import BasePlayer as Player
from.round_iterator import RoundIterator
import logging
import logging.config
import json

with open('config/logging.json', 'r') as f:
    config = json.load(f)

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

class Dealer:
    def __init__(self, player_money: dict[Player, int], BIG_BLIND: int):   
        logger.info(f"Initializing dealer with big blind: {BIG_BLIND} and no. players: {len(player_money)}")
        self.player_money = player_money               #! remember player_money should be in the correct order
        assert len(self.player_money) >= 2, "At least two players are required to play poker."  
        self.BIG_BLIND: Final = BIG_BLIND      
        self.one_player_left = False                  
        self.history = History(BIG_BLIND)
        self.deck = deck()
        self.active_players = {player: True for player in self.player_money}
        self.end_round = False
        self.players_asked = 0
        self.pot: int = 0
        self.player_cards: dict = {}
        self.community_cards: list = []
        self.current_bet = {     
            player: (
                BIG_BLIND//2 if i == 0 else
                BIG_BLIND if i == 1 else
                0
            )
            for i, player in enumerate(self.player_money)
        }
        

    def play(self):
        logger.info("starting game")

        for round in ('preflop', 'flop', 'turn', 'river'):
            if round == 'preflop':
                player_keys = list(self.player_money)               
                self.player_money[player_keys[0]] -= self.BIG_BLIND // 2
                self.player_money[player_keys[1]] -= self.BIG_BLIND  

                logger.info("Dealing preflop cards")
                for player in self.player_money:
                    card1, card2 = self.deck.pop(0), self.deck.pop(0)
                    self.player_cards[player] = [card1, card2]
                    logger.info(f"{player.name} received cards: {self.player_cards[player][0]}, {self.player_cards[player][1]}")
                    player.hand([card1, card2])
                self.history.last_move_amount = self.BIG_BLIND

                self.round(list(self.player_money)[2:]+ list(self.player_money)[:2]) # start the round with the players after the big blind and small blind

            elif round == 'flop':
                self.players_asked = 0
                logger.info("Dealing flop cards")
                self.community_cards.extend([self.deck[0], self.deck[1], self.deck[2]])
                for player in self.player_money:
                    player.flop([self.deck[0], self.deck[1], self.deck[2]])
                del self.deck[:3]
                self.history.last_move_amount = 0
            elif round == 'turn':
                self.players_asked = 0
                logger.info("Dealing turn card")
                self.community_cards.append(self.deck[0])
                for player in self.player_money:
                    player.turn(self.deck[0])
                del self.deck[0]
                self.history.last_move_amount = 0
            elif round == 'river':
                self.players_asked = 0
                logger.info("Dealing river card")
                self.community_cards.append(self.deck[0])
                for player in self.player_money:
                    player.river(self.deck[0])
                del self.deck[0]
                self.history.last_move_amount = 0
            
            self.end_round = False

            if round != 'preflop':  
                self.round(list(self.player_money))
            
        else:          # this means there will be a showdown between the remaining players
            logger.info("Showdown initiated, evaluating hands")
            logger.info(f"Community card: {self.community_cards[0]}, {self.community_cards[1]}, {self.community_cards[2]}, {self.community_cards[3]}, {self.community_cards[4]}")
            return showdown()  #TODO: workout which players to add ass parameters and stuff like that

            '''
            best_hands  = []

            for player in self.player_money:
                if self.active_players[player]:
                    if len(best_hands) == 0:
                        best_hands.append(self.player_cards[player] + self.community_cards)
                    elif len(best_hands) > 0:  
                        potential_best_hands  = self.showdown(best_hands[0], self.player_cards[player] + self.community_cards)
                        if len(potential_best_hands) > 1:  # if there are multiple best hands, handles draws           
                            best_hands.append(self.player_cards[player] + self.community_cards)
                        elif potential_best_hands == [self.player_cards[player] + self.community_cards]:  # if the current hand is better than the previous best hand
                            best_hands = [self.player_cards[player] + self.community_cards]

            if len(best_hands) > 1:  # if there are multiple best hands, handles draws  #! add all in
                winners = []
                player_count = len(best_hands)
                player_winnings = self.pot // player_count
                winning_cards = []
                for hand in best_hands:
                    winning_cards.extend(x for x in hand if x not in self.community_cards)
                for player in self.player_money:
                    if self.player_cards[player] in winning_cards:
                        self.player_money[player] += player_winnings
                        player.draw(player_winnings)
                        winners.append(player)
                logger.info("Draw")
                logger.info(f"{self.player_money.values()}")
                return

            winner_cards = [x for x in best_hands[0] if x not in self.community_cards]

            winner = next(k for k, v in self.player_cards.items() if v == winner_cards)
            self.player_money[winner] += self.pot  # give the winner the pot
            logger.info(f"winner is {winner.name}")
            winner.win(self.pot)  
            logger.info(f"{self.player_money.values()}")
            return'''

    
    def to_pot_transaction(self, player: Player, amount: int):
        player.placed_bet(amount)
        self.player_money[player] -= amount
        self.current_bet[player] += amount
        logger.info(f"{player.name} placed bet of {amount}, remaining money: {self.player_money[player]}")

    def to_player_transaction(self, player: Player, amount: int):
        player.win(amount)
        self.player_money[player] += amount
        self.current_bet[player] -= amount
        logger.info(f"{player.name} won {amount}, current money: {self.player_money[player]}")
        
    def round(self, players: List[Player]):
        round_iterator = RoundIterator(players)      # will iterate over the players in the round, until all players have either folded or called the same amount
        for player in round_iterator:
            if self.active_players[player]:  
                move = player.decision(self.history)
                logger.info(f"{(player.name)} made a move: {move.action}, current bet: {self.current_bet[player]}")
                logger.info(f"pot : {self.pot}")
                if move.action == Action.FOLD: 
                    self.active_players[player] = False
                    logger.info(f"{player.name} folded, remaining players: {list(self.active_players.values()).count(True)}")
                    
                    if list(self.active_players.values()).count(True) == 1:  # this means only one player is left
                        
                        logger.info(f"one player left, ending round")

                        for amount in self.current_bet.values():
                            self.pot += amount 
                        

                        for player in self.player_money:
                            if self.active_players[player]:
                                player.win(self.pot)
                                return
                            
                    bets = [self.current_bet[p] for p in self.player_money if self.active_players[p]]  
                    if (len(set(bets)) == 1) and (self.players_asked == sum(self.active_players.values())):          
                        round_iterator.running = False  # this means all players have folded, so we can end the round
                    
                elif move.action == Action.CALL:
                    self.players_asked += 1
                    logger.info(f"{player.name} called with amount: {self.history.last_move_amount}")
                    if self.history.last_move_amount < self.player_money[player]:
                        player.placed_bet((self.history.last_move_amount - self.current_bet[player]))
                        self.player_money[player] -= (self.history.last_move_amount - self.current_bet[player])
                        self.current_bet[player] = self.history.last_move_amount
                        self.history.last_move_amount = self.current_bet[player]
                    else:            #! makes the player fold, need to impliment all in 

                        logger.warning(f"{player.name} does not have enough money to call, folding")

                        self.active_players[player] = False

                        if list(self.active_players.values()).count(True) == 1:  # this means only one player is left

                            logger.info(f"one player left, ending round")

                            for amount in self.current_bet.values():
                                self.pot += amount

                            for player in self.player_money:
                                if self.active_players[player]:
                                    player.win(self.pot)
                                    self.one_player_left = True
                                    return

                    bets = [self.current_bet[p] for p in self.player_money if self.active_players[p]]  
                    if (len(set(bets)) == 1) and (self.players_asked == sum(self.active_players.values())):  
                        round_iterator.running = False  # this means all players have called the same amount, so we can end the round

                elif move.action == Action.RAISE:
                    self.players_asked += 1
                    logger.info(f"{player.name} raised amount: {move.amount}, last move amount: {self.history.last_move_amount}")
                    raise_amount = move.amount  
                    if raise_amount < self.history.last_raise:   # last_raise will be BIG_BLIND if no raises have been made yet
                        logger.error("Raise amount must be greater than the last raise amount.")
                        raise ValueError("Raise amount must be greater or equal to the last raise amount.")  
                    
                    elif (raise_amount + self.history.last_move_amount) - self.current_bet[player] >= self.player_money[player]:
                        logger.error("Raise amount cannot be greater than the player's remaining money.")
                        raise ValueError("Raise amount cannot be greater than the player's remaining money.")

                    else:
                        self.to_pot_transaction(player, raise_amount + self.history.last_move_amount - self.current_bet[player])
                        '''
                        self.player_money[player] -= (raise_amount + self.history.last_move_amount) - self.current_bet[player]
                        self.current_bet[player] = raise_amount + self.history.last_move_amount'''
                        self.history.last_raise = raise_amount

        for amount in self.current_bet.values():
            self.pot += amount

        self.current_bet = {player: 0 for player in self.player_money}  # reset the current bet for the next round
