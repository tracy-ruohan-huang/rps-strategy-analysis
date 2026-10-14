import random
import itertools
import csv
import os
import time

# Define the moves and the strategies
MOVES = ['Rock', 'Paper', 'Scissors']

def random_strategy(history, opponent_history):
    return random.choice(MOVES)

def constant_strategy(history, opponent_history):
    return 'Rock'  # Constant strategy can be Rock, Paper, or Scissors

def sequential_strategy(history, opponent_history):
    if not history:
        return 'Rock'
    last_move = history[-1]
    return MOVES[(MOVES.index(last_move) + 1) % 3]

def mirror_strategy(history, opponent_history):
    if not opponent_history:
        return random.choice(MOVES)
    return opponent_history[-1]

def exclusion_strategy(history, opponent_history):
    if not opponent_history:
        return random.choice(MOVES)
    last_opponent_move = opponent_history[-1]
    return MOVES[(MOVES.index(last_opponent_move) + 1) % 3]

def reaction_strategy(history, opponent_history):
    if not opponent_history:
        return random.choice(MOVES)
    last_opponent_move = opponent_history[-1]
    return MOVES[(MOVES.index(last_opponent_move) + 2) % 3]

def reverse_mirror_strategy(history, opponent_history):
    if not opponent_history:
        return random.choice(MOVES)
    last_opponent_move = opponent_history[-1]
    return MOVES[(MOVES.index(last_opponent_move) + 2) % 3]

def probability_weighted_strategy(history, opponent_history):
    if not opponent_history:
        return random.choice(MOVES)
    count = {move: opponent_history.count(move) for move in MOVES}
    total = sum(count.values())
    weights = [count[move]/total for move in MOVES]
    return random.choices(MOVES, weights=weights)[0]

def multi_round_observation_strategy(history, opponent_history):
    if len(opponent_history) < 3:
        return random.choice(MOVES)
    last_three_moves = opponent_history[-3:]
    if last_three_moves == ['Rock', 'Rock', 'Rock']:
        return 'Paper'
    elif last_three_moves == ['Paper', 'Paper', 'Paper']:
        return 'Scissors'
    elif last_three_moves == ['Scissors', 'Scissors', 'Scissors']:
        return 'Rock'
    return random.choice(MOVES)

# Mapping strategy names to functions
strategies = {
    'Random': random_strategy,
    'Constant': constant_strategy,
    'Sequential': sequential_strategy,
    'Mirror': mirror_strategy,
    'Exclusion': exclusion_strategy,
    'Reaction': reaction_strategy,
    'Reverse_Mirror': reverse_mirror_strategy,
    'Probability_Weighted': probability_weighted_strategy,
    'Multi_Round_Observation': multi_round_observation_strategy
}

def play_round(strategy1, strategy2, history1, history2):
    move1 = strategy1(history1, history2)
    move2 = strategy2(history2, history1)
    history1.append(move1)
    history2.append(move2)
    if move1 == move2:
        return 0, 0
    elif (move1 == 'Rock' and move2 == 'Scissors') or (move1 == 'Paper' and move2 == 'Rock') or (move1 == 'Scissors' and move2 == 'Paper'):
        return 1, 0
    else:
        return 0, 1

def simulate_match(strategy1, strategy2, num_rounds):
    history1 = []
    history2 = []
    score1, score2 = 0, 0
    for _ in range(num_rounds):
        result1, result2 = play_round(strategy1, strategy2, history1, history2)
        score1 += result1
        score2 += result2
    return score1, score2

def main():
    total_start_time = time.time()
    results = []
    strategy_names = list(strategies.keys())
    rounds = [50, 500, 5000, 50000]

    for num_rounds in rounds:
        print(f"Simulating matches for {num_rounds} rounds...")
        start_time = time.time()
        expected_time = 0
        for i, (strategy_name1, strategy_name2) in enumerate(itertools.product(strategy_names, repeat=2), start=1):
            strategy1 = strategies[strategy_name1]
            strategy2 = strategies[strategy_name2]
            match_start_time = time.time()
            score1, score2 = simulate_match(strategy1, strategy2, num_rounds)
            results.append([num_rounds, strategy_name1, strategy_name2, score1, score2])
            match_end_time = time.time()
            expected_time += match_end_time - match_start_time
            if i % 10 == 0 or i == len(strategy_names)**2:
                elapsed_time = match_end_time - start_time
                print(f"Progress: {i}/{len(strategy_names)**2} matches completed for {num_rounds} rounds. Time elapsed: {elapsed_time:.2f} seconds. Expected time for completion: {expected_time/i*(len(strategy_names)**2-i):.2f} seconds.")

        end_time = time.time()
        total_elapsed_time = end_time - start_time
        print(f"Total time elapsed for {num_rounds} rounds: {total_elapsed_time:.2f} seconds.")

    # Ensure the directory exists
    os.makedirs('WinRPS/data', exist_ok=True)

    # Write results to a CSV file
    with open('WinRPS/data/rps_2players_results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Rounds', 'Strategy 1', 'Strategy 2', 'Score 1', 'Score 2'])
        writer.writerows(results)

    total_end_time = time.time()
    total_time_elapsed = total_end_time - total_start_time
    print(f"Total time elapsed for all simulations: {total_time_elapsed:.2f} seconds.")
    print("All simulations completed and results saved to 'WinRPS/data/rps_results.csv'.")

if __name__ == "__main__":
    main()
