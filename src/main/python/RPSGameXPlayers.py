import random
import csv
from datetime import datetime
import os
import itertools  # Change 1: Import itertools

# Constants representing the moves
ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
MOVES = [ROCK, PAPER, SCISSORS]

# Define strategies
def random_strategy(history, my_history):
    return random.choice(MOVES)

def constant_strategy(history, my_history):
    return ROCK

def sequential_strategy(history, my_history):
    if not my_history:
        return ROCK
    last_move = my_history[-1]
    if last_move == ROCK:
        return PAPER
    elif last_move == PAPER:
        return SCISSORS
    elif last_move == SCISSORS:
        return ROCK

def mirror_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    return history[-1]

def exclusion_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    last_move = history[-1]
    return random.choice([move for move in MOVES if move != last_move])

def reaction_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    last_move = history[-1]
    if last_move == ROCK:
        return PAPER
    elif last_move == PAPER:
        return SCISSORS
    elif last_move == SCISSORS:
        return ROCK

def reverse_mirror_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    last_move = history[-1]
    if last_move == ROCK:
        return SCISSORS
    elif last_move == PAPER:
        return ROCK
    elif last_move == SCISSORS:
        return PAPER

def probability_weighted_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    count_rock = history.count(ROCK)
    count_paper = history.count(PAPER)
    count_scissors = history.count(SCISSORS)
    total = len(history)
    prob_rock = count_rock / total
    prob_paper = count_paper / total
    prob_scissors = count_scissors / total
    move = random.choices(MOVES, weights=[prob_paper, prob_scissors, prob_rock])[0]
    return move

def multi_round_observation_strategy(history, my_history, rounds_to_observe=5):
    if len(history) < rounds_to_observe:
        return random.choice(MOVES)
    recent_moves = history[-rounds_to_observe:]
    count_rock = recent_moves.count(ROCK)
    count_paper = recent_moves.count(PAPER)
    count_scissors = recent_moves.count(SCISSORS)
    if count_rock > count_paper and count_rock > count_scissors:
        return PAPER  # Beat Rock
    elif count_paper > count_rock and count_paper > count_scissors:
        return SCISSORS  # Beat Paper
    elif count_scissors > count_rock and count_scissors > count_paper:
        return ROCK  # Beat Scissors
    else:
        return random.choice(MOVES)  # In case of a tie, choose randomly

# List of strategy functions
strategies = [
    random_strategy,
    constant_strategy,
    sequential_strategy,
    mirror_strategy,
    exclusion_strategy,
    reaction_strategy,
    reverse_mirror_strategy,
    probability_weighted_strategy,
    multi_round_observation_strategy
]

strategy_names = [
    "Random Strategy",
    "Constant Strategy",
    "Sequential Strategy",
    "Mirror Strategy",
    "Exclusion Strategy",
    "Reaction Strategy",
    "Reverse Mirror Strategy",
    "Probability-Weighted Strategy",
    "Multi-Round Observation Strategy"
]

def determine_winner(move1, move2):
    """
    Determine the winner of a single round.
    """
    if move1 == move2:
        return 0  # Draw
    elif (move1 == ROCK and move2 == SCISSORS) or \
         (move1 == PAPER and move2 == ROCK) or \
         (move1 == SCISSORS and move2 == PAPER):
        return 1  # Player 1 wins
    else:
        return 2  # Player 2 wins

def determine_multiplayer_winner(moves):
    """
    Determine the winner in a multi-player game.
    """
    move_counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}

    for move in moves:
        # Convert move to tuple if it's a list
        move_key = tuple(move) if isinstance(move, list) else move

        if move_key in move_counts:
            move_counts[move_key] += 1
        else:
            # Handle unexpected moves if necessary
            print(f"Unexpected move: {move}")

    # Determine the winner based on move counts
    if (move_counts[ROCK] > 0 and move_counts[PAPER] > 0 and move_counts[SCISSORS] > 0) or \
       (move_counts[ROCK] == move_counts[PAPER] == move_counts[SCISSORS]):
        return 0  # Draw

    if move_counts[ROCK] > 0 and move_counts[PAPER] > 0 and move_counts[SCISSORS] == 0:
        return PAPER  # Paper wins
    if move_counts[ROCK] > 0 and move_counts[PAPER] == 0 and move_counts[SCISSORS] > 0:
        return ROCK  # Rock wins
    if move_counts[ROCK] == 0 and move_counts[PAPER] > 0 and move_counts[SCISSORS] > 0:
        return SCISSORS  # Scissors wins

def simulate_multiplayer_match(player_strategies, rounds):
    """
    Simulate a match between multiple players with different strategies for a given number of rounds.
    """
    histories = [[] for _ in player_strategies]
    results = {i: 0 for i in range(len(player_strategies))}
    draws = 0

    for _ in range(rounds):
        moves = [strategy(histories[:i] + histories[i+1:], histories[i]) for i, strategy in enumerate(player_strategies)]
        winner_move = determine_multiplayer_winner(moves)
        if winner_move == 0:
            draws += 1
        else:
            for i, move in enumerate(moves):
                if move == winner_move:
                    results[i] += 1

        for i, move in enumerate(moves):
            histories[i].append(move)

    # Calculate probabilities
    prob_wins = {i: (results[i] / rounds) * 100 for i in results}
    prob_draw = (draws / rounds) * 100

    return results, prob_wins, prob_draw, draws

def simulate_all_multiplayer_matches(rounds, num_players):
    """
    Simulate all strategy matchups for a given number of rounds and players, and save results to a file.
    """
    results = []

    for player_combination in itertools.product(strategies, repeat=num_players):  # Change 1: Use itertools.product
        match_result, prob_wins, prob_draw, draws = simulate_multiplayer_match(player_combination, rounds)
        result_entry = {f"P{i+1} Strat": strategy_names[strategies.index(strategy)] for i, strategy in enumerate(player_combination)}
        result_entry.update({f"P{i+1} Wins": match_result[i] for i in match_result})
        result_entry.update({f"P{i+1} Win %": f"{prob_wins[i]:.2f}%" for i in prob_wins})
        result_entry["Draws"] = draws  # Change 2: Correct variable name to "draws"
        result_entry["Draw %"] = f"{prob_draw:.2f}%"
        results.append(result_entry)

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Directory path
    directory = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data'))

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Full file path
    filename = os.path.join(directory, f'rps_multiplayer_results_{rounds}rounds_{timestamp}.csv')

    # Write results to a CSV file
    with open(filename, 'w', newline='') as file:
        fieldnames = [f"P{i+1} Strat" for i in range(num_players)] + \
                     [f"P{i+1} Wins" for i in range(num_players)] + \
                     [f"P{i+1} Win %" for i in range(num_players)] + \
                     ["Draws", "Draw %"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {filename}")

# Run the simulation for different round counts with multiple players
round_counts = [50, 500, 5000, 50000]

for rounds in round_counts:
    simulate_all_multiplayer_matches(rounds, num_players=3)  # Adjust num_players as needed