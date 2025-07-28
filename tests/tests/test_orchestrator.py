import json
from pathlib import Path
from src.orchestrator import Orchestrator

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

    # 3. Run a few steps and check that it returns a valid macro
    # This history ensures 'macro_A' is chosen next
    orchestrator.history = [{'macro': 'macro_A', 'reward': 1}] 
    result = orchestrator.run_single_step()
    assert result in sample_config["macros"]
    
    # 4. Force a loop condition and verify the guard triggers
    # Simulate 'macro_A' being chosen repeatedly with no score improvement
    orchestrator.history = [
        {'macro': 'macro_A', 'score': 0.5, 'reward': 1},
        {'macro': 'macro_A', 'score': 0.5, 'reward': 1}
    ]
    # The next step will also choose 'macro_A' with no score improvement,
    # which should trigger the loop guard (N=3).
    result = orchestrator.run_single_step()
    assert result == "fallback"
