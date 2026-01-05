from poker.dealer import Dealer
from poker.players.check_player import RandomPlayer
 #TODO: make logs folder if not made already

random_player1 = RandomPlayer("Player 1", 100, 2)
random_player2 = RandomPlayer("Player 2", 100, 2)

player_money = {random_player1: random_player1.money, 
                random_player2: random_player2.money}

dealer = Dealer(player_money, 2)

dealer.play()

print(f"{random_player1.name} has {random_player1.money} money left.")
print(f"{random_player2.name} has {random_player2.money} money left.")