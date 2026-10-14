from history import History

def test_history():
    # Initialize history with default 5-round limit
    history = History()
    
    # Simulate recording moves for multiple rounds
    moves_round_1 = [(0, "rock"), (1, "paper")]
    moves_round_2 = [(0, "scissors"), (1, "rock")]
    moves_round_3 = [(0, "paper"), (1, "scissors")]
    
    history.record_moves(moves_round_1)
    history.record_moves(moves_round_2)
    history.record_moves(moves_round_3)

    # Print out the full history after all rounds
    full_history = history.get_full_history()
    print("Full History after all rounds:")
    for record in full_history:
        print(record)

# Run the test function
if __name__ == "__main__":
    test_history()