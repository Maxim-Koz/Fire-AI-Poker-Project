import pygame
import sys
import logging
import logging.config
import json
from poker.dealer import Dealer
from poker.players.human_player import HumanPlayer
from poker.players.bot_player import BotPlayer
from components.button import Button
from components.textbox import TextBox
from components.database import create_users_table, check_user, add_user
from poker import Action, Move

pygame.init()

# Configure logging
with open("config/logging.json", "r") as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


def format_history(history):
    """Format game history into a human-readable string."""
    if not history.moves:
        return "No moves yet"

    moves_str = []
    for move in history.moves:
        player_name = move.player.name
        action = move.action.value.upper()
        amount = move.amount
        if amount > 0:
            moves_str.append(f"{player_name} {action} {amount}")
        else:
            moves_str.append(f"{player_name} {action}")

    return " → ".join(moves_str)


create_users_table()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Poker")

BG = pygame.image.load("assets/Background.png")
BG = pygame.transform.scale(BG, (1280, 720))

POKER_BG = pygame.image.load("assets/poker_bg.jpg")
POKER_BG = pygame.transform.scale(POKER_BG, (1280, 720))

helper_img = pygame.image.load("assets/poker_help.jpg")
helper_img = pygame.transform.scale(helper_img, (550, 720))

cards_sheet = pygame.image.load("assets/cards/main_cards.png").convert_alpha()


show_helper = False

raising = False  # will allow the user to input raise amount

show_cards = False

initialized_game = False


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def get_card(sheet, col, row, width, height):
    rect = pygame.Rect(col * width, row * height, width, height)
    card = pygame.Surface((width, height), pygame.SRCALPHA)
    card.blit(sheet, (0, 0), rect)
    return card


cards = []

for row in range(4):
    row_cards = []
    for col in range(13):
        card = get_card(cards_sheet, col, row, 48, 64)
        row_cards.append(card)
    cards.append(row_cards)

username_box = TextBox(440, 250, 400, 50, get_font(40), "Username")
password_box = TextBox(440, 350, 400, 50, get_font(40), "Password", password=True)

raise_box = TextBox(900, 200, 310, 50, get_font(25), "Raise Amount")

BUTTON_IMG = pygame.image.load("assets/button.png")

money_box = TextBox(340, 250, 600, 50, get_font(40), "Starting Money")
blind_box = TextBox(340, 350, 600, 50, get_font(40), "Big Blind")
player1_name_box = TextBox(340, 450, 600, 50, get_font(40), "Player 1 Name")
player2_name_box = TextBox(340, 550, 600, 50, get_font(40), "Player 2 Name")

confirm_button = Button(
    image=BUTTON_IMG,
    pos=(640, 650),
    text_input="Start Game",
    font=get_font(40),
    base_color="White",
    hovering_color="Green",
)


# ---------------- LOGIN SCREEN ----------------
def login_screen(events):
    SCREEN.blit(BG, (0, 0))

    mouse_pos = pygame.mouse.get_pos()

    title = get_font(80).render("Login Screen", True, "White")
    SCREEN.blit(title, title.get_rect(center=(640, 150)))

    for event in events:
        username_box.handle_event(event)
        password_box.handle_event(event)

    username_box.draw(SCREEN)
    password_box.draw(SCREEN)

    enter_button = Button(
        image=BUTTON_IMG,
        pos=(400, 500),
        text_input="Enter",
        font=get_font(60),
        base_color="White",
        hovering_color="Green",
    )

    register_button = Button(
        image=BUTTON_IMG,
        pos=(900, 500),
        text_input="Register",
        font=get_font(60),
        base_color="White",
        hovering_color="Green",
    )

    quit_button = Button(
        image=BUTTON_IMG,
        pos=(600, 600),
        text_input="Quit",
        font=get_font(75),
        base_color="White",
        hovering_color="Green",
    )

    enter_button.change_color(mouse_pos)
    enter_button.update(SCREEN)
    quit_button.change_color(mouse_pos)
    quit_button.update(SCREEN)
    register_button.change_color(mouse_pos)
    register_button.update(SCREEN)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if enter_button.check_for_input(mouse_pos):
                username = username_box.text
                password = password_box.text
                if check_user(username, password):
                    return "menu"  # ← Switch screen
            if quit_button.check_for_input(mouse_pos):
                pygame.quit()
                sys.exit()
            if register_button.check_for_input(mouse_pos):
                username = username_box.text
                password = password_box.text
                add_user(username, password)

    return "login"


# ---------------- MAIN MENU ----------------
def menu_screen(events):
    SCREEN.blit(BG, (0, 0))

    mouse_pos = pygame.mouse.get_pos()

    title = get_font(100).render("Poker", True, "White")
    SCREEN.blit(title, title.get_rect(center=(640, 120)))

    playbot_button = Button(
        image=BUTTON_IMG,
        pos=(640, 300),
        text_input="Play Bot",
        font=get_font(75),
        base_color="White",
        hovering_color="Green",
    )

    playhuman_button = Button(
        image=BUTTON_IMG,
        pos=(640, 400),
        text_input="Play Human",
        font=get_font(75),
        base_color="White",
        hovering_color="Green",
    )

    quit_button = Button(
        image=BUTTON_IMG,
        pos=(640, 500),
        text_input="Quit",
        font=get_font(75),
        base_color="White",
        hovering_color="Green",
    )

    for button in [playbot_button, playhuman_button, quit_button]:
        button.change_color(mouse_pos)
        button.update(SCREEN)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button.check_for_input(mouse_pos):
                pygame.quit()
                sys.exit()
            if playbot_button.check_for_input(mouse_pos):
                return "setup_bot"
            if playhuman_button.check_for_input(mouse_pos):
                return "setup_human"
    return "menu"


# ----------------- SETUP GAME -----------------
def setup_screen(events, mode):
    SCREEN.blit(BG, (0, 0))

    mouse_pos = pygame.mouse.get_pos()

    title = get_font(70).render("Game Setup", True, "White")
    SCREEN.blit(title, title.get_rect(center=(640, 150)))

    for event in events:
        money_box.handle_event(event)
        blind_box.handle_event(event)
        player1_name_box.handle_event(event)
        player2_name_box.handle_event(event)

    money_box.draw(SCREEN)
    blind_box.draw(SCREEN)

    if mode == "human":
        player1_name_box.draw(SCREEN)
        player2_name_box.draw(SCREEN)

    confirm_button.change_color(mouse_pos)
    confirm_button.update(SCREEN)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if confirm_button.check_for_input(mouse_pos):
                try:
                    global starting_money
                    global big_blind

                    starting_money = int(money_box.text)
                    big_blind = int(blind_box.text)

                    if (big_blind % 2 != 0) or (big_blind > starting_money):
                        raise ValueError(
                            "Big blind must be an even number and less than or equal to starting money"
                        )

                    if mode == "bot":
                        return "bot_game_loop"
                    else:
                        global player1_name
                        global player2_name
                        player1_name = (
                            player1_name_box.text
                            if player1_name_box.text
                            else "Player 1"
                        )
                        player2_name = (
                            player2_name_box.text
                            if player2_name_box.text
                            else "Player 2"
                        )

                        assert player1_name != player2_name, (
                            "Player names must be different"
                        )
                        assert len(player1_name) <= 8 and len(player2_name) <= 8, (
                            "Player names must be at most 5 characters long"
                        )
                        return "human_game_loop"

                except ValueError as ve:
                    print(f"Invalid input: {ve}")

    return "setup_" + mode


# --------------- MAIN GAME LOOP ------------------
def game_loop(events, which_game):
    global show_cards
    global initialized_game
    global show_helper
    global dealer
    global player1
    global player2
    global raising

    if which_game == "bot_game_loop":
        if not initialized_game:
            player1 = HumanPlayer("You", starting_money, big_blind)
            player2 = BotPlayer("Bot", starting_money, big_blind)
            player_money = {player1: starting_money, player2: starting_money}
            dealer = Dealer(player_money, big_blind)
            initialized_game = True

    elif which_game == "human_game_loop":
        if not initialized_game:
            player1 = HumanPlayer(player1_name, starting_money, big_blind)
            player2 = HumanPlayer(player2_name, starting_money, big_blind)
            player_money = {player1: starting_money, player2: starting_money}
            dealer = Dealer(player_money, big_blind)
            initialized_game = True

    round = dealer.current_round

    current_player = dealer.current_player.peek()

    SCREEN.blit(POKER_BG, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    # Store the pot before round_end resets it
    if (
        hasattr(dealer, "pot")
        and not hasattr(dealer, "final_pot")
        and round == "river"
        and dealer.players_asked >= 2
        and dealer.current_bet[player1] == dealer.current_bet[player2]
    ):
        dealer.final_pot = dealer.pot

    if current_player == player1:
        player1_title = get_font(30).render(player1.name, True, "Yellow")
        player2_title = get_font(30).render(player2.name, True, "White")
    else:
        player1_title = get_font(30).render(player1.name, True, "White")
        player2_title = get_font(30).render(player2.name, True, "Yellow")
    SCREEN.blit(player1_title, (10, 650))
    SCREEN.blit(player2_title, (700, 100))

    money1 = get_font(20).render("money", True, "White")
    money2 = get_font(20).render("money", True, "White")
    SCREEN.blit(money1, (310, 600))
    SCREEN.blit(money2, (1000, 50))

    player1_money = get_font(30).render(
        str(dealer.player_money[player1]), True, "White"
    )
    player2_money = get_font(30).render(
        str(dealer.player_money[player2]), True, "White"
    )
    SCREEN.blit(player1_money, (330, 650))
    SCREEN.blit(player2_money, (1020, 100))

    bet1 = get_font(20).render("bet", True, "White")
    bet2 = get_font(20).render("bet", True, "White")
    SCREEN.blit(bet1, (460, 600))
    SCREEN.blit(bet2, (1150, 50))

    player1_bet = get_font(30).render(str(dealer.current_bet[player1]), True, "White")
    player2_bet = get_font(30).render(str(dealer.current_bet[player2]), True, "White")
    SCREEN.blit(player1_bet, (460, 650))
    SCREEN.blit(player2_bet, (1150, 100))

    pot_title = get_font(20).render("pot", True, "Grey")
    SCREEN.blit(pot_title, (60, 250))
    pot_amount = get_font(30).render(str(dealer.pot), True, "Grey")
    SCREEN.blit(pot_amount, (60, 300))

    round_title = get_font(40).render(
        round if round else "Start Game", True, "light blue"
    )
    SCREEN.blit(round_title, round_title.get_rect(center=(250, 50)))

    check_button = Button(
        image=BUTTON_IMG,
        pos=(1100, 500),
        text_input="Check",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    fold_button = Button(
        image=BUTTON_IMG,
        pos=(1100, 650),
        text_input="Fold",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    call_button = Button(
        image=BUTTON_IMG,
        pos=(1100, 550),
        text_input="Call",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    raise_button = Button(
        image=BUTTON_IMG,
        pos=(1100, 600),
        text_input="Raise",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    back_button = Button(
        image=BUTTON_IMG,
        pos=(100, 100),
        text_input="Back",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    help_button = Button(
        image=BUTTON_IMG,
        pos=(100, 150),
        text_input="Help",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    start_button = None
    if round is None:
        start_button = Button(
            image=BUTTON_IMG,
            pos=(600, 360),
            text_input="Start",
            font=get_font(75),
            base_color="White",
            hovering_color="Green",
        )

    raise_confirm_button = Button(
        image=BUTTON_IMG,
        pos=(1100, 300),
        text_input="Confirm",
        font=get_font(30),
        base_color="White",
        hovering_color="Green",
    )

    show_cards_button = Button(
        image=BUTTON_IMG,
        pos=(140, 200),
        text_input="Show Cards",
        font=get_font(20),
        base_color="White",
        hovering_color="Green",
    )

    buttons = [
        check_button,
        fold_button,
        call_button,
        raise_button,
        back_button,
        help_button,
    ]
    if start_button:
        buttons.append(start_button)
    if round is not None:
        buttons.append(show_cards_button)
    if raising:
        buttons.append(raise_confirm_button)
        raise_box.draw(SCREEN)

    for button in buttons:
        button.change_color(mouse_pos)
        button.update(SCREEN)

    # Handle bot moves automatically
    if (
        which_game == "bot_game_loop"
        and current_player == player2
        and round is not None
    ):
        if dealer.player_move_decisions[player2] is None:
            try:
                bot_move = player2.decision(dealer.history)
                dealer.player_move_decisions[player2] = bot_move

                if bot_move.action == Action.FOLD:
                    dealer.player_moved(player2, bot_move)
                    logger.info(
                        f"Bot {player2.name} folded. History: {format_history(dealer.history)}"
                    )
                    dealer.active_players[player2] = False
                    next(dealer.current_player)
                    dealer.players_asked += 1

                    # Check if only one player is left
                    active = [p for p, alive in dealer.active_players.items() if alive]
                    if len(active) == 1:
                        dealer.winners = {
                            active[0]: dealer.player_cards.get(active[0], [])
                        }
                        if not hasattr(dealer, "final_pot"):
                            dealer.final_pot = dealer.pot
                        dealer.round_end()
                        return "end_game"

                elif bot_move.action == Action.CALL:
                    highest_bet = max(dealer.current_bet.values())
                    call_amount = highest_bet - dealer.current_bet[player2]
                    dealer.player_moved(player2, bot_move)
                    logger.info(
                        f"Bot {player2.name} called {call_amount}. History: {format_history(dealer.history)}"
                    )
                    dealer.current_bet[player2] = highest_bet
                    next(dealer.current_player)
                    dealer.players_asked += 1

                elif bot_move.action == Action.RAISE:
                    # Bot wants to raise
                    raise_amount = bot_move.amount
                    available_money = dealer.player_money[player2]

                    # Check if bot has enough money to raise
                    if raise_amount > available_money:
                        # Not enough money, call instead
                        print(
                            f"Bot cannot raise {raise_amount}, only has {available_money}, calling instead"
                        )
                        highest_bet = max(dealer.current_bet.values())
                        call_amount = highest_bet - dealer.current_bet[player2]
                        call_move = Move(player2, Action.CALL, call_amount)
                        dealer.player_moved(player2, call_move)
                        dealer.current_bet[player2] = highest_bet
                    else:
                        # Can raise
                        dealer.player_moved(player2, bot_move)
                        logger.info(
                            f"Bot {player2.name} raised {bot_move.amount}. History: {format_history(dealer.history)}"
                        )

                    next(dealer.current_player)
                    dealer.players_asked += 1
            except Exception as e:
                print(f"Bot decision error: {e}")
                bot_fold = Move(player2, Action.FOLD, 0)
                dealer.player_moved(player2, bot_fold)
                logger.info(
                    f"Bot {player2.name} folded due to error. History: {format_history(dealer.history)}"
                )
                dealer.active_players[player2] = False
                next(dealer.current_player)
                dealer.players_asked += 1

    for event in events:
        if raising:
            raise_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if check_button.check_for_input(mouse_pos):
                try:
                    assert dealer.current_bet[player1] == dealer.current_bet[player2], (
                        "Players must have given the same amount to check"
                    )
                    check_amount = dealer.current_bet[current_player]
                    player_move = Move(current_player, Action.CALL, check_amount)
                    dealer.player_moved(current_player, player_move)
                    logger.info(
                        f"Player {current_player.name} checked. History: {format_history(dealer.history)}"
                    )
                    next(dealer.current_player)
                    dealer.players_asked += 1
                except Exception as e:
                    print(f"Check error: {e}")

            if fold_button.check_for_input(mouse_pos):
                player_move = Move(current_player, Action.FOLD, 0)
                dealer.player_moved(current_player, player_move)
                logger.info(
                    f"Player {current_player.name} folded. History: {format_history(dealer.history)}"
                )
                dealer.active_players[current_player] = False
                next(dealer.current_player)
                dealer.players_asked += 1

                # Check if only one player is left
                active = [p for p, alive in dealer.active_players.items() if alive]
                if len(active) == 1:
                    dealer.winners = {active[0]: dealer.player_cards.get(active[0], [])}
                    if not hasattr(dealer, "final_pot"):
                        dealer.final_pot = dealer.pot
                    dealer.round_end()
                    print(dealer.winners)
                    return "end_game"

            if call_button.check_for_input(mouse_pos):
                try:
                    highest_bet = max(dealer.current_bet.values())
                    call_amount = highest_bet - dealer.current_bet[current_player]
                    player_move = Move(current_player, Action.CALL, call_amount)
                    dealer.player_moved(current_player, player_move)
                    logger.info(
                        f"Player {current_player.name} called {call_amount}. History: {format_history(dealer.history)}"
                    )
                    dealer.current_bet[current_player] = highest_bet
                    next(dealer.current_player)
                    dealer.players_asked += 1
                    # Reset opponent's decision since bet level changed
                    dealer.player_move_decisions[player2] = None
                except Exception as e:
                    print(f"Call error: {e}")

            if raise_button.check_for_input(mouse_pos):
                raising = True

            if raise_confirm_button.check_for_input(mouse_pos) and raising:
                try:
                    raise_amount = int(raise_box.text)
                except ValueError:
                    print("Invalid raise amount")
                    return which_game

                if raise_amount < big_blind:
                    print(f"Raise must be at least {big_blind}")
                    return which_game

                # Check if player has enough money to raise
                available_money = (
                    dealer.player_money[current_player]
                    - dealer.current_bet[current_player]
                )
                if raise_amount > available_money:
                    print(
                        f"Insufficient funds. You only have {available_money} available to raise"
                    )
                    return which_game

                try:
                    raise_to_pay = raise_amount
                    player_move = Move(current_player, Action.RAISE, raise_to_pay)
                    dealer.player_moved(current_player, player_move)
                    logger.info(
                        f"Player {current_player.name} raised {raise_to_pay}. History: {format_history(dealer.history)}"
                    )
                    next(dealer.current_player)
                    dealer.players_asked += 1
                    raising = False
                    # Reset opponent's decision since bet level changed
                    dealer.player_move_decisions[player2] = None
                except Exception as e:
                    print(f"Raise error: {e}")

            if back_button.check_for_input(mouse_pos):
                # Reset all game state variables
                show_cards = False
                initialized_game = False
                show_helper = False
                raising = False
                dealer = None
                player1 = None
                player2 = None

                # Clear textboxes
                money_box.text = ""
                blind_box.text = ""
                player1_name_box.text = ""
                player2_name_box.text = ""
                raise_box.text = ""

                return "menu"

            if help_button.check_for_input(mouse_pos):
                show_helper = not show_helper

            if start_button and start_button.check_for_input(mouse_pos):
                dealer.current_round = "preflop"

            if show_cards_button.check_for_input(mouse_pos):
                show_cards = not show_cards

    if show_helper:
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))

        rect = helper_img.get_rect(center=(640, 360))
        SCREEN.blit(helper_img, rect)

    card_mapping = {
        "H": 0,
        "D": 1,
        "S": 2,
        "C": 3,
        "A": 0,
        "2": 1,
        "3": 2,
        "4": 3,
        "5": 4,
        "6": 5,
        "7": 6,
        "8": 7,
        "9": 8,
        "T": 9,
        "J": 10,
        "Q": 11,
        "K": 12,
    }

    if round != "preflop" and len(dealer.community_cards) > 0:
        card1 = dealer.community_cards[0]
        card2 = dealer.community_cards[1]
        card3 = dealer.community_cards[2]

        ncard1_num = (
            card_mapping[card1.rank.value] + 13 * card_mapping[card1.suit.value]
        )
        ncard2_num = (
            card_mapping[card2.rank.value] + 13 * card_mapping[card2.suit.value]
        )
        ncard3_num = (
            card_mapping[card3.rank.value] + 13 * card_mapping[card3.suit.value]
        )

        community_card1 = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard1_num}.png"
        ).get_rect(center=(400, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard1_num}.png"
            ),
            community_card1,
        )
        community_card2 = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard2_num}.png"
        ).get_rect(center=(500, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard2_num}.png"
            ),
            community_card2,
        )
        community_card3 = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard3_num}.png"
        ).get_rect(center=(600, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard3_num}.png"
            ),
            community_card3,
        )
    if round in ["turn", "river"] and len(dealer.community_cards) > 3:
        card4 = dealer.community_cards[3]
        ncard4_num = (
            card_mapping[card4.rank.value] + 13 * card_mapping[card4.suit.value]
        )

        community_card4 = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard4_num}.png"
        ).get_rect(center=(700, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard4_num}.png"
            ),
            community_card4,
        )
    if round == "river" and len(dealer.community_cards) > 4:
        card5 = dealer.community_cards[4]
        ncard5_num = (
            card_mapping[card5.rank.value] + 13 * card_mapping[card5.suit.value]
        )

        community_card5 = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard5_num}.png"
        ).get_rect(center=(800, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard5_num}.png"
            ),
            community_card5,
        )

    if (
        dealer.players_asked >= len(dealer.player_money)
        and len(set(dealer.current_bet.values())) == 1
    ):  # all players have been asked at least once and bets are equal
        # move the bets into the pot and reset state so a new
        # betting cycle can start on the next round
        for amount in list(dealer.current_bet.values()):
            dealer.pot += amount
        dealer.current_bet = {player: 0 for player in dealer.player_money}
        dealer.players_asked = 0
        # Reset player move decisions for new round
        dealer.player_move_decisions = {player: None for player in dealer.player_money}

        # Advance round
        if dealer.current_round == "preflop":
            dealer.current_round = "flop"
            if not dealer.player_cards:
                dealer.deal_cards("preflop")
            if len(dealer.community_cards) == 0:
                dealer.deal_cards("flop")
        elif dealer.current_round == "flop":
            dealer.current_round = "turn"
            if len(dealer.community_cards) == 3:
                dealer.deal_cards("turn")
        elif dealer.current_round == "turn":
            dealer.current_round = "river"
            if len(dealer.community_cards) == 4:
                dealer.deal_cards("river")
        elif dealer.current_round == "river":
            if not hasattr(dealer, "final_pot"):
                dealer.final_pot = dealer.pot
            dealer.round_end()
            print(dealer.winners)
            return "end_game"

    if round == "preflop":
        if (
            dealer.players_asked >= 2
            and dealer.current_bet[player1] == dealer.current_bet[player2]
        ):
            dealer.players_asked = 0
            # Reset player move decisions for new round
            dealer.player_move_decisions = {
                player: None for player in dealer.player_money
            }
            dealer.current_round = "flop"

        if not dealer.player_cards:
            dealer.deal_cards("preflop")

    elif round == "flop":
        if (
            dealer.players_asked >= 2
            and dealer.current_bet[player1] == dealer.current_bet[player2]
        ):
            dealer.players_asked = 0
            # Reset player move decisions for new round
            dealer.player_move_decisions = {
                player: None for player in dealer.player_money
            }
            dealer.current_round = "turn"

        if len(dealer.community_cards) == 0:
            dealer.deal_cards("flop")
        pass
    elif round == "turn":
        if (
            dealer.players_asked >= 2
            and dealer.current_bet[player1] == dealer.current_bet[player2]
        ):
            dealer.players_asked = 0
            # Reset player move decisions for new round
            dealer.player_move_decisions = {
                player: None for player in dealer.player_money
            }
            dealer.current_round = "river"

        if len(dealer.community_cards) == 3:
            dealer.deal_cards("turn")
        pass
    elif round == "river":
        if (
            dealer.players_asked >= 2
            and dealer.current_bet[player1] == dealer.current_bet[player2]
        ):
            if not hasattr(dealer, "final_pot"):
                dealer.final_pot = dealer.pot
            dealer.round_end()
            print(dealer.winners)
            return "end_game"

        if len(dealer.community_cards) == 4:
            dealer.deal_cards("river")
        pass

    if show_cards:
        hole_cards = current_player.hole_cards

        card1 = hole_cards[0]
        card2 = hole_cards[1]

        card1_num = card_mapping[card1.rank.value] + 13 * card_mapping[card1.suit.value]
        card2_num = card_mapping[card2.rank.value] + 13 * card_mapping[card2.suit.value]

        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))

        player_card1 = pygame.image.load(
            f"assets/cards/large_individual_cards/large_card_{'%02d' % card1_num}.png"
        ).get_rect(center=(400, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/large_individual_cards/large_card_{'%02d' % card1_num}.png"
            ),
            player_card1,
        )

        player_card2 = pygame.image.load(
            f"assets/cards/large_individual_cards/large_card_{'%02d' % card2_num}.png"
        ).get_rect(center=(800, 360))
        SCREEN.blit(
            pygame.image.load(
                f"assets/cards/large_individual_cards/large_card_{'%02d' % card2_num}.png"
            ),
            player_card2,
        )

    return which_game


# --------------- MAIN BOT GAME LOOP ------------------
def bot_game_loop(events):
    return game_loop(events, "bot_game_loop")


# ---------------- MAIN HUMAN GAME LOOP ------------------
def human_game_loop(events):
    return game_loop(events, "human_game_loop")


# ---------------- END GAME LOOP ------------------
def end_game_loop(events):
    global show_cards
    global initialized_game
    global show_helper
    global dealer
    global player1
    global player2
    global raising

    SCREEN.blit(BG, (0, 0))

    title = get_font(80).render("Game Over", True, "White")
    SCREEN.blit(title, title.get_rect(center=(640, 50)))

    back_button = Button(
        image=BUTTON_IMG,
        pos=(640, 650),
        text_input="Back to Menu",
        font=get_font(30),
        base_color="White",
        hovering_color="Green",
    )

    for button in [back_button]:
        button.change_color(pygame.mouse.get_pos())
        button.update(SCREEN)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.check_for_input(pygame.mouse.get_pos()):
                # Reset all game state variables
                show_cards = False
                initialized_game = False
                show_helper = False
                raising = False
                dealer = None
                player1 = None
                player2 = None

                # Clear textboxes
                money_box.text = ""
                blind_box.text = ""
                player1_name_box.text = ""
                player2_name_box.text = ""
                raise_box.text = ""

                return "menu"

    card_mapping = {
        "H": 0,
        "D": 1,
        "S": 2,
        "C": 3,
        "A": 0,
        "2": 1,
        "3": 2,
        "4": 3,
        "5": 4,
        "6": 5,
        "7": 6,
        "8": 7,
        "9": 8,
        "T": 9,
        "J": 10,
        "Q": 11,
        "K": 12,
    }

    # Always show all 5 community cards, even if round ended early
    community_title = get_font(30).render("Community Cards", True, "White")
    SCREEN.blit(community_title, community_title.get_rect(center=(640, 240)))

    # If fewer than 5 cards, deal the rest from the deck for display
    shown_community = list(dealer.community_cards)
    if len(shown_community) < 5 and hasattr(dealer, "deck"):
        # Get remaining cards from deck (without modifying the real deck)
        deck_copy = list(dealer.deck)
        while len(shown_community) < 5 and deck_copy:
            shown_community.append(deck_copy.pop(0))

    for i, card in enumerate(shown_community[:5]):
        ncard_num = card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
        card_img = pygame.image.load(
            f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
        )
        SCREEN.blit(card_img, card_img.get_rect(center=(400 + i * 120, 340)))

    # Rest of end screen logic unchanged
    if len(dealer.winners) == 2:
        draw_text = get_font(50).render("It's a Draw!", True, "Yellow")
        SCREEN.blit(draw_text, draw_text.get_rect(center=(640, 120)))

        # Use the final pot value if available
        pot = getattr(dealer, "final_pot", dealer.pot if hasattr(dealer, "pot") else 0)
        winnings = pot // 2
        winnings_text = get_font(30).render(
            f"Each player wins: {winnings}", True, "Green"
        )
        SCREEN.blit(winnings_text, winnings_text.get_rect(center=(640, 160)))

        # Player 1 cards
        p1_text = get_font(25).render(f"{player1.name}", True, "White")
        SCREEN.blit(p1_text, (100, 240))
        if hasattr(player1, "hole_cards") and len(player1.hole_cards) >= 2:
            for i, card in enumerate(player1.hole_cards[:2]):
                ncard_num = (
                    card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
                )
                card_img = pygame.image.load(
                    f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
                )
                SCREEN.blit(card_img, card_img.get_rect(center=(120 + i * 120, 340)))

        # Player 2 cards
        p2_text = get_font(25).render(f"{player2.name}", True, "White")
        SCREEN.blit(p2_text, (1020, 240))
        if hasattr(player2, "hole_cards") and len(player2.hole_cards) >= 2:
            for i, card in enumerate(player2.hole_cards[:2]):
                ncard_num = (
                    card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
                )
                card_img = pygame.image.load(
                    f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
                )
                SCREEN.blit(card_img, card_img.get_rect(center=(1040 + i * 120, 340)))

        winning_title = get_font(30).render("Tied Hand", True, "White")
        SCREEN.blit(winning_title, winning_title.get_rect(center=(640, 490)))

        winner_hand = list(dealer.winners.values())[0]
        if winner_hand and len(winner_hand) > 0:
            for i, card in enumerate(winner_hand[:5]):
                ncard_num = (
                    card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
                )
                card_img = pygame.image.load(
                    f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
                )
                SCREEN.blit(card_img, card_img.get_rect(center=(400 + i * 120, 570)))
        else:
            # If no hand stored, construct it from shown_community cards
            for i, card in enumerate(shown_community[:5]):
                ncard_num = (
                    card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
                )
                card_img = pygame.image.load(
                    f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
                )
                SCREEN.blit(card_img, card_img.get_rect(center=(400 + i * 120, 570)))

        return "end_game"

    winner_player = list(dealer.winners.keys())[0]
    winner_name = winner_player.name
    is_fold = len(dealer.winners[winner_player]) == 0  # Empty hand means fold

    pot = getattr(dealer, "final_pot", dealer.pot if hasattr(dealer, "pot") else 0)
    winnings = pot

    if is_fold:
        fold_text = get_font(40).render(f"{winner_name} wins by fold!", True, "Green")
        SCREEN.blit(fold_text, fold_text.get_rect(center=(640, 120)))

        opponent = player2 if winner_player == player1 else player1
        opponent_text = get_font(25).render(f"({opponent.name} folded)", True, "Yellow")
        SCREEN.blit(opponent_text, opponent_text.get_rect(center=(640, 170)))

        winnings_text = get_font(30).render(
            f"{winner_name} wins: {winnings}", True, "Green"
        )
        SCREEN.blit(winnings_text, winnings_text.get_rect(center=(640, 210)))
    else:
        winner_text = get_font(40).render(f"Winner: {winner_name}", True, "Green")
        SCREEN.blit(winner_text, winner_text.get_rect(center=(640, 120)))

        winnings_text = get_font(30).render(
            f"{winner_name} wins: {winnings}", True, "Green"
        )
        SCREEN.blit(winnings_text, winnings_text.get_rect(center=(640, 170)))

    # Player 1 cards
    p1_text = get_font(25).render(f"{player1.name}", True, "White")
    SCREEN.blit(p1_text, (100, 240))
    if hasattr(player1, "hole_cards") and len(player1.hole_cards) >= 2:
        for i, card in enumerate(player1.hole_cards[:2]):
            ncard_num = (
                card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
            )
            card_img = pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
            )
            SCREEN.blit(card_img, card_img.get_rect(center=(120 + i * 120, 340)))

    # Player 2 cards
    p2_text = get_font(25).render(f"{player2.name}", True, "White")
    SCREEN.blit(p2_text, (1020, 240))
    if hasattr(player2, "hole_cards") and len(player2.hole_cards) >= 2:
        for i, card in enumerate(player2.hole_cards[:2]):
            ncard_num = (
                card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
            )
            card_img = pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
            )
            SCREEN.blit(card_img, card_img.get_rect(center=(1040 + i * 120, 340)))

    winning_title = get_font(30).render("Winning Hand", True, "White")
    SCREEN.blit(winning_title, winning_title.get_rect(center=(640, 490)))

    winner_hand = list(dealer.winners.values())[0]
    if winner_hand:
        for i, card in enumerate(winner_hand[:5]):
            ncard_num = (
                card_mapping[card.rank.value] + 13 * card_mapping[card.suit.value]
            )
            card_img = pygame.image.load(
                f"assets/cards/normal_individual_cards/card_{'%02d' % ncard_num}.png"
            )
            SCREEN.blit(card_img, card_img.get_rect(center=(400 + i * 120, 570)))

    return "end_game"


# ---------------- GAME SCREEN LOOP ----------------
def main():
    clock = pygame.time.Clock()
    current_screen = "login"

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if current_screen == "login":
            current_screen = login_screen(events)

        elif current_screen == "menu":
            current_screen = menu_screen(events)

        elif current_screen == "bot_game_loop":
            current_screen = bot_game_loop(events)

        elif current_screen == "human_game_loop":
            current_screen = human_game_loop(events)

        elif current_screen == "setup_bot":
            current_screen = setup_screen(events, "bot")

        elif current_screen == "setup_human":
            current_screen = setup_screen(events, "human")

        elif current_screen == "end_game":
            current_screen = end_game_loop(events)

        pygame.display.update()
        clock.tick(60)


main()
