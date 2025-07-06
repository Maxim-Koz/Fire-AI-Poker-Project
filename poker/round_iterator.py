from typing import Collection

class RoundIterator:
    def __init__(self, players: Collection):
        self.players = list(players)
        self.current_index = 0
        self.running = True

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.running:
            raise StopIteration
        
        player = self.players[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.players)
        return player