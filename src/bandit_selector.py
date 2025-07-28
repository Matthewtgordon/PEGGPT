import random


def choose_macro(macros, history):
    """
    Chooses the best macro using a Thompson Sampling bandit algorithm.

    Args:
        macros (list of str): A list of available macro names (the "arms").
        history (list of dicts): A list of past actions. Each dict should have
                                 'macro' and 'reward' (0 for fail, 1 for success) keys.

    Returns:
        str: The name of the chosen macro.
    """
    arm_stats = {macro: {'successes': 1, 'failures': 1} for macro in macros}  # Start with Beta(1,1) prior

    # Update stats based on historical data
    for record in history:
        macro_name = record.get('macro')
        reward = record.get('reward')
        if macro_name in arm_stats:
            if reward == 1:
                arm_stats[macro_name]['successes'] += 1
            elif reward == 0:
                arm_stats[macro_name]['failures'] += 1

    # Thompson Sampling: sample from each arm's Beta distribution
    best_macro = None
    max_sample = -1

    for macro, stats in arm_stats.items():
        # Sample from a Beta distribution using the successes (alpha) and failures (beta)
        sample = random.betavariate(stats['successes'], stats['failures'])
        if sample > max_sample:
            max_sample = sample
            best_macro = macro

    return best_macro
