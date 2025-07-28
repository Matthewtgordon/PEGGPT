import json
import sys
import os
from pathlib import Path

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from orchestrator import Orchestrator

def test_orchestrator_integration(tmp_path: Path):
    """
    Tests that the orchestrator correctly uses the selector and loop guard
    based on the session configuration.
    """
    # 1. Create a sample config file in a temporary directory
    sample_config = {
        "macros": ["macro_A", "macro_B"],
        "selector": {"algorithm": "bandit_ts"},
        "loop_guard": {"enabled": True, "N": 3, "epsilon": 0.02}
    }
    config_file = tmp_path / "TestConfig.json"
    with config_file.open('w') as f:
        json.dump(sample_config, f)

    # 2. Initialize the orchestrator with the test config
    orchestrator = Orchestrator(config_file)

    # 3. Force a loop condition by running the same macro 3 times
    orchestrator.history = [
        {'macro': 'macro_A', 'score': 0.5, 'reward': 1},
        {'macro': 'macro_A', 'score': 0.5, 'reward': 1},
        {'macro': 'macro_A', 'score': 0.5, 'reward': 1}
    ]
    
    # 4. NOW, on the next step, the loop guard should trigger
    # The history contains 3 consecutive non-improving steps, so this
    # run_single_step() call should detect the loop and return "fallback".
    result = orchestrator.run_single_step()
    assert result == "fallback"
