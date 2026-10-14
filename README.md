# Poker: Computer Science NEA

A Python poker game where you can play heads-up (1v1) against a friend or against an AI opponent.

<img src="assets/Screenshots/Screenshot1.png" alt="Poker game screenshot" width="600">

## Features

- **Two-player mode:** choose both players' starting chips and the big blind
- **Single-player mode:** play against a neural-network-based bot
- Full poker logic, including hand evaluation and comparison

## Built With

- Python
- Pygame (UI)
- TensorFlow / Keras (AI)
- mypy (static type checking)

## Getting Started

```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt
python main.py
```

## How It Works

I built the poker logic first: hand encoding, hand evaluation, and comparing two players' hands against the community cards.

I then built the bot. Because of time constraints I kept it fairly simple. Given its two cards and the current community cards, a neural network outputs a number between 0 and 1 representing how strong the hand is (0 weakest, 1 strongest). The network has an input layer encoding the cards, three hidden layers, and a single output.

For training data I generated 100,000 hands, labelled by which hand wins, and split them about 80 / 20 for training and testing.

### Limitations and Future Work

The bot's accuracy on the test set was was lower than I'd hoped, and I ran out of time to improve it. If I returned to it, I would change how the bot decides which action to pick. For a value of hand p, I made the bot fold if p<0.3, call if 0.3<=p<0.5 and raise if 0.5<=p with raises being proportional to p ( p=1.0 would be all in). These bounds are fixed and not informed by much so the next step would be to base the decision on the pot odds rather than a fixed threshold. 

## Challenges

This was my first major Python project, so I had to get used to new tools like mypy and logging. Time constraints meant I couldn't do everything I wanted, and the AI is the part I'd most like to improve.

## What I Learned

How to structure a larger project, the value of mypy and log files, better git habits, and how to build a simple neural network.

## Screenshots

<img src="assets/Screenshots/Screenshot2.png" alt="Poker" width="450"> &nbsp; <img src="assets/Screenshots/Screenshot3.png" alt="Poker" width="450">

<img src="assets/Screenshots/Screenshot4.png" alt="Poker" width="450"> &nbsp; <img src="assets/Screenshots/Screenshot5.png" alt="Poker" width="450">
