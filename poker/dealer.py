from typing import Dict, Final, Collection, List
import numpy as np
from . import deck, Card, Action
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
        self.play_end = False                
        self.history = History(BIG_BLIND)
        self.winners: Dict[Player, List[Card]] = {}
        self.deck = deck() 
        self.active_players = {player: True for player in self.player_money} 
        self.players_asked = 0 
        self.pot: int = 0 
        self.player_cards: dict = {}
        self.community_cards: list = [] 
        self.current_bet = {player: 0 for player in self.player_money}
        

    def play(self):
        logger.info("starting game")
        self.round(list(self.player_money)[2:]+ list(self.player_money)[:2], 'preflop') # start the round with the players after the big blind and small blind
        if self.round_end():
            return
        self.round(self.player_money, 'flop')
        if self.round_end():
            return
        self.round(self.player_money, 'turn')
        if self.round_end():
            return
        self.round(self.player_money, 'river')
        if self.round_end():
            return
        
        logger.info("Showdown initiated, evaluating hands")
        logger.info(f"Community card: {self.community_cards[0]}, {self.community_cards[1]}, {self.community_cards[2]}, {self.community_cards[3]}, {self.community_cards[4]}")

        self.play_end = True
        self.round_end()


    def round(self, players: Collection[Player], round: str):
        if round == 'preflop':
            player_keys = list(self.player_money)               
            self.to_pot_transaction(player_keys[0], self.BIG_BLIND // 2)  # small blind
            self.to_pot_transaction(player_keys[1], self.BIG_BLIND)  # big blind

            logger.info("Dealing preflop cards")
            for player in self.player_money:
                card1, card2 = self.deck.pop(0), self.deck.pop(0)
                self.player_cards[player] = [card1, card2]
                logger.info(f"{player.name} received cards: {self.player_cards[player][0]}, {self.player_cards[player][1]}")
                player.hand([card1, card2])
            self.history.last_move_amount = self.BIG_BLIND
        elif round == 'flop':
            self.players_asked = 0
            logger.info("Dealing flop cards")
            card1, card2, card3 = self.deck.pop(0), self.deck.pop(0), self.deck.pop(0)
            self.community_cards.extend([card1, card2, card3])
            for player in self.player_money:
                player.flop([card1, card2, card3])
            self.history.last_move_amount = 0
        else:
            self.players_asked = 0
            card1 = self.deck.pop(0)
            self.community_cards.append(card1)
            for player in self.player_money:
                player.turn(card1)
            self.history.last_move_amount = 0

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
                                self.one_player_left = True
                                self.winners = showdown({player: self.player_cards[player]})
                                return
                            
                    bets = [self.current_bet[p] for p in self.player_money if self.active_players[p]]  
                    if (len(set(bets)) == 1) and (self.players_asked == sum(self.active_players.values())):          
                        round_iterator.running = False  # this means all players have folded, so we can end the round
                    
                elif move.action == Action.CALL:
                    self.players_asked += 1
                    logger.info(f"{player.name} called with amount: {self.history.last_move_amount}")
                    if self.history.last_move_amount < self.player_money[player]:
                        self.to_pot_transaction(player, self.history.last_move_amount - self.current_bet[player])
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
                                    self.one_player_left = True
                                    self.winners = showdown({player: self.player_cards[player]})
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
                        self.history.last_raise = raise_amount

        for amount in self.current_bet.values():
            self.pot += amount

        self.current_bet = {player: 0 for player in self.player_money}  # reset the current bet for the next round


    def to_pot_transaction(self, player: Player, amount: int):
        player.placed_bet(amount)
        self.player_money[player] -= amount
        self.current_bet[player] += amount
        logger.info(f"{player.name} placed bet of {amount}, remaining money: {self.player_money[player]}")

    def to_player_transaction(self, player: Player, amount: int):
        player.win(amount)
        self.player_money[player] += amount
        self.current_bet[player] -= amount
        self.pot -= amount
        logger.info(f"{player.name} won {amount}")
        

    def round_end(self) -> bool:
        if self.one_player_left or self.play_end: 
            potential_winners = {}
            for player in self.player_cards:
                if self.active_players[player]:
                    potential_winners[player] = self.player_cards[player] + self.community_cards    

            self.winners = showdown(potential_winners)  

            share = self.pot // len(self.winners)
            remainder = self.pot % len(self.winners)  #? could change what happens to remainder based on settings, for now it is given to first player left of the dealer

            for player in self.winners:
                self.to_player_transaction(player, share)

            for player in self.player_money:
                if self.active_players[player]:
                    self.to_player_transaction(player, remainder)
                    break
            for player in self.player_money:
                if not(self.active_players[player]):
                    player.loose(self.winners)
            
            for player in self.player_money:
                logger.info(f"{player.name} finished game with {self.player_money[player]}")
            
            return True
        return False