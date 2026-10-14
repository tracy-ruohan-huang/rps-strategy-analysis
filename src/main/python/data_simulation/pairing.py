from config import config

class Pairing:
    def __init__(self, strategies, pair_size=config["pairing"]["pair_size"], rule=config["pairing"]["rule"]):
        """
        Initializes the Pairing instance.
        
        Parameters:
        - strategies (List[Strategy]): List of strategy instances to be paired.
        - pair_size (int): Number of players per pairing, default set in config.
        - rule (str): Rule for pairing generation (e.g., "round-robin"), default set in config.
        """
        self.strategies = strategies
        self.pair_size = pair_size
        self.rule = rule

    def generate_pairs(self):
        """
        Generates pairs based on the specified rule.
        
        Returns:
        - List[Tuple[str, List[Strategy]]]: A list of tuples, each containing a unique pairing ID (pid)
          and a list of strategies in the pair.
        """
        if self.rule == "round-robin":
            return self.round_robin_pairs()
        else:
            raise ValueError(f"Unsupported pairing rule: {self.rule}")

    def generate_pid(self, strategies):
        """
        Generates a unique pairing ID (pid) based on strategy IDs in the group.
        
        Parameters:
        - strategies (List[Strategy]): List of strategies in the pair.

        Returns:
        - str: A unique pairing ID for the group, based on sorted strategy IDs.
        """
        strategy_ids = sorted(strategy.id for strategy in strategies)
        return ''.join(map(str, strategy_ids))

    def round_robin_pairs(self):
        """
        Generates all unique pairs (or groups) based on a round-robin rule.
        
        Returns:
        - List[Tuple[str, List[Strategy]]]: A list of tuples, where each tuple contains a pid
          and a list of strategies in the pair or group.
        """
        pairs = []
        num_strategies = len(self.strategies)

        # Generate round-robin pairs/groups for the specified pair size
        for i in range(num_strategies):
            for j in range(i, num_strategies):
                selected_strategies = [self.strategies[i], self.strategies[j]]
                
                # If pair_size is greater than 2, extend selection
                if self.pair_size > 2:
                    for k in range(j, num_strategies):
                        if len(selected_strategies) < self.pair_size:
                            selected_strategies.append(self.strategies[k])
                
                # Only add pairs that meet the specified pair size
                if len(selected_strategies) == self.pair_size:
                    pid = self.generate_pid(selected_strategies)
                    pairs.append((pid, selected_strategies))
        
        return pairs
