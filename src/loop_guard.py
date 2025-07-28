def detect_loop(history, N=3, epsilon=0.02):
    """
    Detects if the same macro has been chosen N times consecutively
    without a score improvement greater than epsilon.

    Args:
        history (list of dicts): A list of past actions. Each dict should have
                                 'macro' and 'score' keys.
        N (int): The number of consecutive repeats to detect as a loop.
        epsilon (float): The minimum score improvement required to be considered
                         "progress".

    Returns:
        bool: True if a loop is detected, False otherwise.
    """
    if len(history) < N:
        return False

    # Get the last N items from the history for checking
    recent_actions = history[-N:]

    # Check if the macro is the same in all recent actions
    last_macro = recent_actions[0].get('macro')
    if not all(action.get('macro') == last_macro for action in recent_actions):
        return False

    # Check if there has been any significant improvement in score
    for i in range(N - 1):
        score_current = recent_actions[i].get('score', 0)
        score_next = recent_actions[i + 1].get('score', 0)
        if (score_next - score_current) > epsilon:
            return False  # Improvement was found, not a loop

    # If the same macro was used N times with no improvement, it's a loop
    return True
