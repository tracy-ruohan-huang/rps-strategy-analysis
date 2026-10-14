# game_tester.py

from game import Game
from strategies import load_strategies
from history import History

def test_game():
    # Load all available strategies and initialize history
    strategies = load_strategies()
    history = History()

    # Select two strategies to test (adjust as necessary)
    selected_strategies = list(strategies.values())[:2]  # Test with first two strategies

    # Print the selected strategies for verification
    print("Selected Strategies for Testing:")
    for strategy in selected_strategies:
        print(f"Strategy ID: {strategy.id}, Abbreviation: {strategy.abbr}, Name: {strategy.name}")

    # Initialize a Game instance with the selected strategies
    game = Game(players=selected_strategies, history=history)

    # Play a few rounds
    print("\nPlaying Game Rounds:")
    num_rounds = 10
    for round_num in range(1, num_rounds + 1):
        print(f"\nRound {round_num}:")
        game.play_round()

        # Display round results
        round_results = game.get_results()
        for player_id, result in round_results.items():
            print(f"Player {result['strategy_id']} ({result['strategy_abbr']}): "
                  f"Wins = {result['wins']}, Draws = {result['draws']}, Losses = {result['losses']}")

    # Display full history for verification
    print("\nHistory after all rounds:")
    for record in history.get_full_history():
        print(record)

if __name__ == "__main__":
    test_game()
