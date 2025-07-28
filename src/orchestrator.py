import json
from pathlib import Path
from bandit_selector import choose_macro
from loop_guard import detect_loop

class Orchestrator:
    def __init__(self, config_path: Path):
        """Initializes the orchestrator with configuration."""
        with config_path.open() as f:
            self.config = json.load(f)
        self.history = []

    def run_single_step(self):
        """
        Runs a single step of the agent's decision-making loop.
        """
        # 1. Check for loops using the Loop Guard BEFORE choosing a new macro
        loop_guard_config = self.config.get('loop_guard', {})
        if loop_guard_config.get('enabled', False):
            is_looping = detect_loop(
                self.history,
                N=loop_guard_config.get('N', 3),
                epsilon=loop_guard_config.get('epsilon', 0.02)
            )
            if is_looping:
                print(
                    f"Loop detected with macro '{self.history[-1]['macro'] if self.history else None}'! Triggering fallback."
                )
                return "fallback"  # Signal that a fallback should be triggered

        # 2. Use the Bandit Selector to choose the next macro
        available_macros = self.config.get('macros', [])
        chosen_macro = choose_macro(available_macros, self.history)

        # 3. Simulate getting a reward for the action
        # (In a real scenario, this would come from a scoring model)
        reward = 1  # Assume success for this example

        # 4. Update the history
        self.history.append({
            'macro': chosen_macro,
            'score': len(self.history) * 0.1,
            'reward': reward
        })

        return chosen_macro

def main():
    """A simple main function to demonstrate the orchestrator."""
    config_file = Path("SessionConfig.json")
    if not config_file.exists():
        print("Error: SessionConfig.json not found.")
        return

    agent_orchestrator = Orchestrator(config_file)
    
    print("Running orchestrator for 10 steps...")
    for i in range(10):
        result = agent_orchestrator.run_single_step()
        print(f"Step {i+1}: Chose macro '{result}'")
        if result == "fallback":
            break
            
if __name__ == "__main__":
    main()
