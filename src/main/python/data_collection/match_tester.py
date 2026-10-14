from strategies import load_strategies
from history import History
from match import load_match_class

def test_match():
    # Load strategies and initialize centralized history
    strategies = load_strategies()
    history = History()  # Create a shared history instance
    
    # Load the match class dynamically based on config
    match_class = load_match_class()
    
    # Initialize the match with the list of strategies and shared history
    match = match_class(strategies=list(strategies.values()), history=history)
    
    # Play the match
    match.play_match()
    
    # Display match results
    print("Match Results:")
    results = match.get_match_results()
    for player_id, result in results.items():
        print(f"Player {result['strategy_id']} ({result['strategy_abbr']}): Wins = {result['wins']}, Draws = {result['draws']}, Losses = {result['losses']}")
    
    # Display history after all rounds
    print("\nFull History after all rounds:")
    full_history = history.get_full_history()
    #for player_id, moves in full_history.items():
    #    print(f"Player {player_id}: {moves}")
    for record in full_history:  # Iterate over list elements directly
        print(record)
if __name__ == "__main__":
    test_match()
