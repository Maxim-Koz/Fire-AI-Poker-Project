from typing import List

class RoundIterator:
    def __init__(self, players: List):
        self.players = players
        self.current_index = 0
        self.running = True

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.running:
            raise StopIteration
        index = self.current_index
        
        if self.current_index == (len(self.players) - 1):  # if we reached the end of the list, we start over
            self.current_index = 0

        return self.players[index]