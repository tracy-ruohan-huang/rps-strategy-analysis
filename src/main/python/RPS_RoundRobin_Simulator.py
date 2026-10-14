import random
import csv
import os
from tqdm import tqdm

# Constants representing the moves
ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
MOVES = [ROCK, PAPER, SCISSORS]

# Constants for strategies
STRATEGY_NAMES = [
    "Random",
    "Constant",
    "Sequential",
    "Mirror",
    "Exclusion",
    "Reaction",
    "ReverseMirror",
    "ProbWeighted",
    "MultiRoundObs"
]

# Define strategies
def random_strategy(history, my_history):
    return random.choice(MOVES)

def constant_strategy(history, my_history):
    return ROCK

def sequential_strategy(history, my_history):
    if not my_history:
        return ROCK
    last_move = my_history[-1]
    return {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}.get(last_move, ROCK)

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
    return {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}.get(last_move, random.choice(MOVES))

def reverse_mirror_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    last_move = history[-1]
    return {ROCK: SCISSORS, PAPER: ROCK, SCISSORS: PAPER}.get(last_move, random.choice(MOVES))

def probability_weighted_strategy(history, my_history):
    if not history:
        return random.choice(MOVES)
    counts = {move: history.count(move) for move in MOVES}
    total = len(history)
    if total == 0:  # Avoid division by zero
        return random.choice(MOVES)
    weights = [counts[move] / total for move in MOVES]
    return random.choices(MOVES, weights=weights)[0]

def multi_round_observation_strategy(history, my_history, rounds_to_observe=5):
    if len(history) < rounds_to_observe:
        return random.choice(MOVES)
    recent_moves = history[-rounds_to_observe:]
    counts = {move: recent_moves.count(move) for move in MOVES}
    if all(count == 0 for count in counts.values()):  # Avoid empty counts
        return random.choice(MOVES)
    max_move = max(counts, key=lambda move: counts[move])
    return {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}.get(max_move, random.choice(MOVES))

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

def determine_winner(move1, move2):
    """
    Determine the winner of a single round.
    """
    if move1 == move2:
        return 0  # Draw
    if (move1 == ROCK and move2 == SCISSORS) or \
       (move1 == PAPER and move2 == ROCK) or \
       (move1 == SCISSORS and move2 == PAPER):
        return 1  # Player 1 wins
    return 2  # Player 2 wins

def simulate_match(strategy1, strategy2, rounds):
    """
    Simulate a match between two strategies for a given number of rounds.
    """
    history1 = []
    history2 = []
    results = {1: 0, 2: 0, 0: 0}  # Wins for Player 1, Player 2, and Draws

    for _ in range(rounds):
        move1 = strategy1(history2, history1)
        move2 = strategy2(history1, history2)
        winner = determine_winner(move1, move2)
        results[winner] += 1
        history1.append(move1)
        history2.append(move2)

    # Calculate win percentages
    prob_p1_win = round((results[1] / rounds) * 100, 2)
    prob_p2_win = round((results[2] / rounds) * 100, 2)
    prob_draw = round((results[0] / rounds) * 100, 2)

    return results, prob_p1_win, prob_p2_win, prob_draw

def simulate_all_matches():
    """
    Simulate all strategy matchups for different numbers of rounds and save results to a file.
    """
    round_intervals = range(10, 1001, 10)
    all_results = []

    for rounds in tqdm(round_intervals, desc="Simulating rounds"):
        for i, strategy1 in enumerate(strategies):
            for j, strategy2 in enumerate(strategies):
                match_result, prob_p1_win, prob_p2_win, prob_draw = simulate_match(strategy1, strategy2, rounds)
                win_rate_diff = round(prob_p1_win - prob_p2_win, 2)
                all_results.append({
                    "Rnd": rounds,
                    "S1": STRATEGY_NAMES[i],
                    "S2": STRATEGY_NAMES[j],
                    "#S1W": match_result[1],
                    "#S2W": match_result[2],
                    "#Drw": match_result[0],
                    "%S1W": prob_p1_win,
                    "%S2W": prob_p2_win,
                    "%Drw": prob_draw,
                    "%WDif": win_rate_diff
                })

    output_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data'))
    output_file_name = 'strategy_simulation_results.csv'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save results to CSV
    output_file = os.path.join(output_dir, output_file_name)
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["Rnd", "S1", "S2", "#S1W", "#S2W", "#Drw", "%S1W", "%S2W", "%Drw", "%WDif"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f'Simulation result has been saved to {output_file}')

# Call the simulation function
simulate_all_matches()
