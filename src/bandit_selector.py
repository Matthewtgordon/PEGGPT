#
# This module contains the bandit-based macro selector for the PEG agent.
# It uses a Thompson Sampling algorithm to learn which macro is most
# effective over time, balancing exploration and exploitation.
#
import random
from typing import List, Dict, Any

def choose_macro(macros: List[str], history: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
    """
    Chooses the best macro using a Thompson Sampling bandit algorithm.

    This function is now robust, filtering the orchestrator's history and
    converting continuous scores into binary rewards for the learning algorithm.

    Args:
        macros (list of str): A list of available macro names (the "arms").
        history (list of dicts): The full history from the orchestrator.
        config (dict): The session configuration, used to get the scoring threshold.

    Returns:
        str: The name of the chosen macro.
    """
    # Initialize stats for each arm with a Beta(1,1) prior, which represents
    # one initial success and one initial failure to avoid extreme probabilities at the start.
    arm_stats = {macro: {'successes': 1, 'failures': 1} for macro in macros}

    # Get the pass/fail threshold from the configuration
    pass_threshold = config.get('ci', {}).get('minimum_score', 0.8)

    # Filter history for relevant 'build' events and update stats
    build_actions = [h for h in history if h.get('node') == 'build' and 'macro' in h]
    
    for record in build_actions:
        macro_name = record.get('macro')
        score = record.get('score')
        
        if macro_name in arm_stats and score is not None:
            # Convert the continuous score into a binary reward
            reward = 1 if score >= pass_threshold else 0
            
            if reward == 1:
                arm_stats[macro_name]['successes'] += 1
            else:
                arm_stats[macro_name]['failures'] += 1

    # --- Thompson Sampling ---
    # For each macro (arm), sample a value from its Beta distribution.
    # The Beta distribution is a good model for the success probability of an arm.
    best_macro = None
    max_sample = -1

    for macro, stats in arm_stats.items():
        # Sample from a Beta distribution using the successes (alpha) and failures (beta)
        sample = random.betavariate(stats['successes'], stats['failures'])
        
        if sample > max_sample:
            max_sample = sample
            best_macro = macro

    # If no macro is chosen for some reason (e.g., empty macro list), default to the first one
    if best_macro is None and macros:
        return macros[0]
        
    return best_macro
