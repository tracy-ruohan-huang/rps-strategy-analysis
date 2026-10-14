import csv
from config import config
from simulation import Simulation
from history import History

def run_simulation_and_output_to_file():
    # Prepare the output file from config
    output_filename = config["simulation"]["output"]["filename"]
    columns = config["simulation"]["output"]["columns"]

    # Open output file for writing
    with open(output_filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        
        # Run simulation for each round count in the specified range
        for rounds in config["simulation"]["rounds"]:
            print(f"\nRunning simulation for {rounds} rounds...")
            
            # Initialize History and Simulation objects
            history = History()
            simulation = Simulation(rounds)
            
            # Run the simulation and capture the results
            results = simulation.run()
            
            # Format results and write to output file
            formatted_results = format_results(rounds, results)
            writer.writerows(formatted_results)
            print(f"Simulation for {rounds} rounds complete. Results saved to {output_filename}.")

def format_results(rounds, results):
    """
    Formats simulation results to match the output file structure.

    Args:
        rounds (int): The number of rounds in the simulation.
        results (list): List of result dictionaries from the simulation.

    Returns:
        list: Formatted results ready for CSV output.
    """
    formatted_results = []
    for result in results:
        formatted_result = {
            "Rnds": rounds,
            "ID": result["strategy_id"],
            "Strategy": result["strategy_abbr"],
            "Wins": result["wins"],
            "Losses": result["losses"],
            "Draws": result["draws"],
            "WR (%)": f"{result['win_rate']:.2f}",
            "DR (%)": f"{result['draw_rate']:.2f}",
            "Avg. WR (%)": f"{result['avg_win_rate']:.2f}",
            "WRD (%)": f"{result['wrd']:.2f}"
        }
        formatted_results.append(formatted_result)
    return formatted_results

# Run the test function
if __name__ == "__main__":
    run_simulation_and_output_to_file()
