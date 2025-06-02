from typing import Sequence ,Final
from . import deck, Card, Move
from .history import History

class Player: 
    pass

BIG_BLIND :Final = 2
class Dealer():
    def __init__(self, players: Sequence[Player]):
        self.players = players
        self.history = History()
        self.active_players = {player: True for player in self.players}  
        self.pot = 0

    
    def play(self):

        # Deal cards to players
        for player in self.players:
            player.hand(deck.pop(0), deck.pop(0))

        current_bet = {}
        player_money = {}  
        folded = {}
        history = []
        removed_players = []


        for player in self.players:
            if self.active_players[player]:
                move = player.decision(history)  
                if move.action == 'fold':
                    folded[player] = True
                    removed_players.append(player)
                    pot += current_bet[player]
                    current_bet[player] = 0
                    history.append([player, move, ])

                if list(folded.values()).count(False) == 1: # check if only one player is left
                        return 
                elif move.action == 'call':
                    pass
                elif move.action == 'raise':
                    pass
            
