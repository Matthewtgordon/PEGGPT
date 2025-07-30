#
# This script is the core "brain" of the PEG agent. It acts as a graph
# execution engine, bringing the process defined in WorkflowGraph.json to life.
# It orchestrates the agent's actions, from intake to final export, and
# integrates all the learning and safety modules.
#
import json
from pathlib import Path
import time
import random # PATCH: Added missing import for random
from datetime import datetime # PATCH: Added import for ISO timestamps

# Import the learning and safety modules
from bandit_selector import choose_macro
from loop_guard import detect_loop
# We will import the main scoring function from run_scoring.py
# from run_scoring import calculate_final_score # (Assumes run_scoring is updated to provide this)

class Orchestrator:
    """
    Executes the workflow defined in WorkflowGraph.json.
    """
    def __init__(self, config_path: Path, workflow_graph_path: Path):
        """Initializes the orchestrator with all necessary configuration files."""
        print("Initializing Orchestrator...")
        with config_path.open(encoding='utf-8') as f:
            self.config = json.load(f)
        with workflow_graph_path.open(encoding='utf-8') as f:
            self.workflow_graph = json.load(f)
        
        # The state holds all the dynamic information for a single run
        self.state = {
            "current_node": self.workflow_graph.get("entry_point", "intake"),
            "history": [],
            "last_score": 0.0,
            "output": None,
            "loop_iterations": 0
        }
        print(f"Orchestrator initialized. Starting at node: '{self.state['current_node']}'")

    def get_node_details(self, node_id: str):
        """Finds the full details for a node by its ID in the graph."""
        for node in self.workflow_graph.get("nodes", []):
            if node.get("id") == node_id:
                return node
        return None

    def get_next_node(self, current_node_id: str, condition: str):
        """Finds the next node in the graph based on the current node and a condition."""
        for edge in self.workflow_graph.get("edges", []):
            if edge.get("from") == current_node_id and edge.get("condition") == condition:
                return edge.get("to")
        # Find an unconditional edge if no conditional one matches
        for edge in self.workflow_graph.get("edges", []):
            if edge.get("from") == current_node_id and "condition" not in edge:
                return edge.get("to")
        return None # No path forward

    def execute_graph(self):
        """
        Runs the main loop that executes the workflow graph until it reaches an end state.
        """
        while self.state["current_node"] is not None and self.state["current_node"] != "__end__":
            node = self.get_node_details(self.state["current_node"])
            if not node:
                print(f"❌ Error: Node '{self.state['current_node']}' not found in workflow graph. Halting.")
                break

            print(f"\n--- Executing Node: {node.get('label', node['id'])} ---")
            
            # --- Execute the action for the current node ---
            # This is where the logic for each step (intake, build, review, etc.) would go.
            # For this example, we'll simulate the actions.
            
            action_result = "success" # Default result
            
            if node['id'] == 'build':
                # In the build step, we use the bandit selector to choose a macro
                available_macros = self.config.get('macros', [])
                chosen_macro = choose_macro(available_macros, self.state['history'])
                print(f"Chosen Macro: '{chosen_macro}'")
                # Simulate the output of the build process
                self.state['output'] = f"Output from {chosen_macro}"
                self.state['loop_iterations'] += 1

            elif node['id'] == 'review':
                # In the review step, we score the output
                # In a real run, this would call the scoring script on self.state['output']
                # score = calculate_final_score(self.state['output']) # Example call
                score = random.uniform(0.7, 1.0) # Simulate a score
                self.state['last_score'] = score
                print(f"Scoring complete. Score: {score:.2f}")

                # Based on the score, we determine if validation passed or failed
                pass_threshold = self.config.get('ci', {}).get('minimum_score', 0.8)
                if score >= pass_threshold:
                    action_result = "score_passed"
                    self.state['loop_iterations'] = 0 # Reset loop counter on success
                else:
                    action_result = "validation_failed"

            elif node['id'] == 'loop_detector':
                # The loop detector checks if we are stuck in a build->review loop
                is_looping = detect_loop(
                    self.state['history'],
                    N=self.config.get('loop_guard', {}).get('N', 3),
                    epsilon=self.config.get('loop_guard', {}).get('epsilon', 0.02)
                )
                action_result = "loop_detected" if is_looping else "loop_not_detected"
                print(f"Loop detection result: {action_result}")
            
            elif node['id'] == 'export':
                 print("✅ Workflow complete. Exporting results.")
                 action_result = "__end__"

            # --- Find the next node based on the action's result ---
            next_node_id = self.get_next_node(node['id'], action_result)
            self.state["current_node"] = next_node_id
            
            # Update history for the learning modules
            self.state['history'].append({
                'node': node['id'],
                'result': action_result,
                'score': self.state['last_score'],
                # PATCH: Changed to ISO format to comply with UTS #35 rule
                'timestamp': datetime.now().isoformat()
            })
            
            if not self.state["current_node"]:
                print(f"--- No further path from node '{node['id']}' with condition '{action_result}'. Halting. ---")


def main():
    """A simple main function to demonstrate the orchestrator."""
    config_file = Path("SessionConfig.json")
    graph_file = Path("WorkflowGraph.json")

    if not config_file.exists() or not graph_file.exists():
        print(f"❌ Error: Make sure SessionConfig.json and WorkflowGraph.json are present.")
        return

    agent_orchestrator = Orchestrator(config_file, graph_file)
    agent_orchestrator.execute_graph()

if __name__ == "__main__":
    main()
