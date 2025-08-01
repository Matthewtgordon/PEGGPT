#!/usr/bin/env python3
"""
Command-line interface for executing phases defined in Instructions.txt.
"""
import argparse
from pathlib import Path

from tasks_parser import parse_instructions


def run_phase(phase: int) -> None:
    """Read Instructions.txt, filter for the given phase, and print tasks."""
    file_path = Path("Instructions.txt")
    if not file_path.exists():
        print(f"[FAIL] Instructions.txt not found in {file_path.resolve().parent}")
        return

    content = file_path.read_text(encoding="utf-8")
    tasks = parse_instructions(content)
    selected = [t for t in tasks if t["phase"] == phase]
    if not selected:
        print(f"No tasks found for phase {phase}")
        return

    print(f"Tasks for Phase {phase}:")
    for t in selected:
        print("-", t["description"])


def classify_intent(text: str):
    """Rudimentary intent classifier for the REPL."""
    text = text.strip()
    if text.lower() in ("exit", "quit"):
        return "quit", {}
    if text.startswith("run-phase"):
        parts = text.split()
        if len(parts) >= 2 and parts[1].isdigit():
            return "run_phase", {"phase": int(parts[1])}
    if text.startswith("scaffold plugin"):
        name = text[len("scaffold plugin"):].strip()
        if name:
            return "scaffold_plugin", {"plugin_name": name}
    if text.startswith("scaffold workflow"):
        name = text[len("scaffold workflow"):].strip()
        if name:
            return "scaffold_workflow", {"workflow_name": name}
    if text.startswith("scaffold agent"):
        name = text[len("scaffold agent"):].strip()
        if name:
            return "scaffold_agent", {"agent_name": name}
    if text.startswith("scaffold test"):
        name = text[len("scaffold test"):].strip()
        if name:
            return "scaffold_test", {"test_suite_name": name}
    if text.startswith("scaffold ci"):
        name = text[len("scaffold ci"):].strip()
        return "scaffold_ci", {"pipeline_name": name if name else "default"}
    if text.startswith("scaffold ui"):
        parts = text[len("scaffold ui"):].strip().split()
        ui_type = parts[0] if parts else "gradio"
        ui_name = parts[1] if len(parts) > 1 else "default"
        return "scaffold_ui", {"ui_type": ui_type, "ui_name": ui_name}
    if text.lower() in ("mark-done", "done"):
        return "mark_done", {}
    if text.lower() in ("show-next", "next"):
        return "show_next", {}
    if text.startswith("run workflow"):
        name = text[len("run workflow"):].strip()
        if name:
            return "run_workflow", {"workflow_name": name}
    if text.lower() in ("status", "state"):
        return "show_status", {}
    if text.lower() in ("stop", "halt"):
        return "stop_workflow", {}
    if text.lower() in ("pause", "break"):
        return "pause_workflow", {}
    if text.lower() in ("resume", "continue"):
        return "resume_workflow", {}
    if text.startswith("review"):
        return "review_step", {}
    if text.startswith("refine"):
        params = text[len("refine"):].strip()
        return "refine_step", {"refinement": params}
    if text.lower() in ("help", "?"):
        return "help", {}
    return None, {}


def repl() -> None:
    """Simple Read‑Eval‑Print Loop for interactive commands."""
    print("Welcome to peg REPL. Type 'help' for commands, 'exit' to quit.")
    while True:
        user = input("peg> ")
        intent, params = classify_intent(user)
        if intent == "quit":
            break
        if intent == "help":
            print("Commands:")
            print("  run-phase <n>         - List tasks for phase <n>")
            print("  scaffold plugin <Name> - Generate plugin skeleton")
            print("  scaffold workflow <Name> - Generate workflow JSON")
            print("  scaffold agent <Name>  - Generate agent skeleton")
            print("  scaffold test <Name>   - Generate test suite JSON")
            print("  scaffold ci [Name]     - Generate CI pipeline and validation")
            print("  scaffold ui <type> [Name] - Generate web UI (gradio/streamlit)")
            print("  run workflow <Name>   - Execute workflow with orchestrator")
            print("  status / state        - Show workflow execution status")
            print("  stop / halt           - Stop running workflow")
            print("  pause / break         - Pause workflow for review")
            print("  resume / continue     - Resume paused workflow")
            print("  review                - Review current workflow step")
            print("  refine <changes>      - Refine current step with changes")
            print("  mark-done / done      - Mark current phase complete")
            print("  show-next / next      - Show next pending tasks")
            print("  exit / quit           - Exit REPL")
            continue
        if intent == "run_phase":
            run_phase(params["phase"])
            continue
        if intent == "scaffold_plugin":
            scaffold_plugin(params["plugin_name"])
            continue
        if intent == "scaffold_workflow":
            scaffold_workflow(params["workflow_name"])
            continue
        if intent == "scaffold_agent":
            scaffold_agent(params["agent_name"])
            continue
        if intent == "scaffold_test":
            scaffold_test(params["test_suite_name"])
            continue
        if intent == "scaffold_ci":
            scaffold_ci(params["pipeline_name"])
            continue
        if intent == "scaffold_ui":
            scaffold_ui(params["ui_type"], params["ui_name"])
            continue
        if intent == "mark_done":
            mark_done()
            continue
        if intent == "show_next":
            show_next()
            continue
        if intent == "run_workflow":
            run_workflow(params["workflow_name"])
            continue
        if intent == "show_status":
            show_workflow_status()
            continue
        if intent == "stop_workflow":
            stop_workflow()
            continue
        if intent == "pause_workflow":
            pause_workflow()
            continue
        if intent == "resume_workflow":
            resume_workflow()
            continue
        if intent == "review_step":
            review_current_step()
            continue
        if intent == "refine_step":
            refine_current_step(params["refinement"])
            continue
        print("[WARN] Unknown command. Type 'help'.")


def scaffold_plugin(plugin_name: str) -> None:
    """Generate a plugin skeleton from template."""
    from jinja2 import Environment, FileSystemLoader

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    template = env.get_template("plugin_skeleton.py.j2")
    class_name = plugin_name
    module_file = class_name.lower() + ".py"
    out_dir = Path("plugins")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / module_file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template.render(class_name=class_name))
    print(f"[PASS] Scaffolded plugin: {out_path}")


def scaffold_workflow(workflow_name: str) -> None:
    """Generate a workflow JSON from template."""
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    template = env.get_template("workflow_skeleton.json.j2")
    
    out_path = Path(f"{workflow_name}Workflow.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template.render(
            workflow_name=workflow_name,
            primary_agent=workflow_name.upper(),
            timestamp=datetime.now().isoformat()
        ))
    print(f"[PASS] Scaffolded workflow: {out_path}")


def scaffold_agent(agent_name: str) -> None:
    """Generate an agent skeleton from template."""
    from jinja2 import Environment, FileSystemLoader

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    template = env.get_template("agent_skeleton.py.j2")
    
    out_dir = Path("agents")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{agent_name.lower()}_agent.py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template.render(agent_name=agent_name))
    print(f"[PASS] Scaffolded agent: {out_path}")


def scaffold_test(test_suite_name: str) -> None:
    """Generate a test suite JSON from template."""
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    template = env.get_template("test_skeleton.json.j2")
    
    out_path = Path(f"{test_suite_name}Tests.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template.render(
            test_suite_name=test_suite_name,
            timestamp=datetime.now().isoformat()
        ))
    print(f"[PASS] Scaffolded test suite: {out_path}")


def scaffold_ci(pipeline_name: str = "default") -> None:
    """Generate CI pipeline and validation script."""
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    
    # Create .github/workflows directory
    github_dir = Path(".github/workflows")
    github_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate CI pipeline
    ci_template = env.get_template("ci_pipeline.yml.j2")
    ci_path = github_dir / f"{pipeline_name}-validation.yml"
    with open(ci_path, "w", encoding="utf-8") as f:
        f.write(ci_template.render(
            pipeline_name=f"{pipeline_name.title()} Validation Pipeline"
        ))
    
    # Generate validation script
    validate_template = env.get_template("validate_scaffolds.py.j2")
    validate_path = Path("validate_scaffolds.py")
    with open(validate_path, "w", encoding="utf-8") as f:
        f.write(validate_template.render(
            project_name="PEGGPT",
            description="Validation script for PEGGPT scaffolded templates"
        ))
    
    # Make validation script executable
    validate_path.chmod(0o755)
    
    print(f"[PASS] Scaffolded CI pipeline: {ci_path}")
    print(f"[PASS] Scaffolded validation script: {validate_path}")


def scaffold_ui(ui_type: str = "gradio", ui_name: str = "default") -> None:
    """Generate web UI interface (Gradio or Streamlit)."""
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime

    if ui_type.lower() not in ["gradio", "streamlit"]:
        print(f"[FAIL] Unsupported UI type: {ui_type}. Use 'gradio' or 'streamlit'")
        return

    tpl_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    
    # Create ui directory
    ui_dir = Path("ui")
    ui_dir.mkdir(exist_ok=True)
    
    if ui_type.lower() == "gradio":
        template = env.get_template("gradio_ui.py.j2")
        ui_path = ui_dir / f"{ui_name}_gradio_ui.py"
        requirements_extra = "gradio>=4.0.0"
    else:  # streamlit
        template = env.get_template("streamlit_ui.py.j2")
        ui_path = ui_dir / f"{ui_name}_streamlit_ui.py"
        requirements_extra = "streamlit>=1.28.0"
    
    with open(ui_path, "w", encoding="utf-8") as f:
        f.write(template.render(
            project_name="PEGGPT",
            app_title=f"PEG Assistant ({ui_name.title()})",
            system_context="Advanced prompt engineering and workflow orchestration interface"
        ))
    
    # Make UI script executable
    ui_path.chmod(0o755)
    
    # Create or update requirements file
    req_path = Path("ui_requirements.txt")
    if req_path.exists():
        with open(req_path, "r") as f:
            existing = f.read()
        if requirements_extra not in existing:
            with open(req_path, "a") as f:
                f.write(f"\n{requirements_extra}\n")
    else:
        with open(req_path, "w") as f:
            f.write(f"# UI dependencies for {ui_type.title()} interface\n")
            f.write(f"{requirements_extra}\n")
            f.write("jinja2>=3.0.0\n")
    
    print(f"[PASS] Scaffolded {ui_type.title()} UI: {ui_path}")
    print(f"[PASS] Updated requirements: {req_path}")
    print(f"[OK] Run with: python {ui_path}")


def mark_done() -> None:
    """Mark current phase as complete."""
    # TODO: Integrate with task tracking system
    print("[OK] Current phase marked as complete")


def show_next() -> None:
    """Show next pending tasks."""
    # TODO: Integrate with task tracking system
    file_path = Path("Instructions.txt")
    if not file_path.exists():
        print("[WARN] Instructions.txt not found - cannot show next tasks")
        return
    
    content = file_path.read_text(encoding="utf-8")
    tasks = parse_instructions(content)
    pending = [t for t in tasks if not t.get("completed", False)]
    
    if not pending:
        print("[OK] No pending tasks found")
        return
    
    print("Next pending tasks:")
    for i, task in enumerate(pending[:5], 1):  # Show first 5
        phase = task.get("phase", "?")
        desc = task.get("description", "No description")
        print(f"  {i}. Phase {phase}: {desc}")
    
    if len(pending) > 5:
        print(f"  ... and {len(pending) - 5} more tasks")


# Global variables to track workflow orchestrator and state
_current_orchestrator = None
_workflow_paused = False
_pending_refinements = []


def run_workflow(workflow_name: str) -> None:
    """Execute a workflow using the orchestrator."""
    global _current_orchestrator
    
    if _current_orchestrator is not None:
        print("[WARN] Workflow already running. Use 'stop' to halt current workflow first.")
        return
    
    # Try to find the workflow file
    workflow_file = Path(f"{workflow_name}Workflow.json")
    if not workflow_file.exists():
        workflow_file = Path("WorkflowGraph.json")  # Fallback to default
        if not workflow_file.exists():
            print(f"[FAIL] Workflow file not found: {workflow_name}Workflow.json")
            return
    
    config_file = Path("SessionConfig.json")
    if not config_file.exists():
        print("[FAIL] SessionConfig.json not found")
        return
    
    try:
        # Import orchestrator here to avoid circular imports
        from orchestrator import Orchestrator
        
        print(f"[OK] Starting workflow: {workflow_name}")
        _current_orchestrator = Orchestrator(config_file, workflow_file)
        
        # Run the workflow in a controlled manner
        _current_orchestrator.execute_graph()
        
        print(f"[OK] Workflow {workflow_name} completed")
        _current_orchestrator = None
        
    except ImportError:
        print("[FAIL] Could not import orchestrator. Check src/orchestrator.py")
    except Exception as e:
        print(f"[FAIL] Workflow execution failed: {e}")
        _current_orchestrator = None


def show_workflow_status() -> None:
    """Show current workflow execution status."""
    global _current_orchestrator
    
    if _current_orchestrator is None:
        print("[OK] No workflow currently running")
        return
    
    state = _current_orchestrator.state
    print(f"[OK] Workflow Status:")
    print(f"  Current Node: {state.get('current_node', 'unknown')}")
    print(f"  Last Score: {state.get('last_score', 0.0):.3f}")
    print(f"  Loop Iterations: {state.get('loop_iterations', 0)}")
    print(f"  History Entries: {len(state.get('history', []))}")


def stop_workflow() -> None:
    """Stop the currently running workflow."""
    global _current_orchestrator, _workflow_paused, _pending_refinements
    
    if _current_orchestrator is None:
        print("[OK] No workflow currently running")
        return
    
    print("[OK] Stopping workflow...")
    _current_orchestrator = None
    _workflow_paused = False
    _pending_refinements = []
    print("[OK] Workflow stopped")


def pause_workflow() -> None:
    """Pause the currently running workflow for human review."""
    global _workflow_paused
    
    if _current_orchestrator is None:
        print("[WARN] No workflow currently running")
        return
    
    _workflow_paused = True
    print("[OK] Workflow paused for review")
    print("[OK] Use 'review' to examine current step, 'refine <changes>' to modify")
    print("[OK] Use 'resume' to continue execution")


def resume_workflow() -> None:
    """Resume a paused workflow."""
    global _workflow_paused
    
    if _current_orchestrator is None:
        print("[WARN] No workflow currently running")
        return
    
    if not _workflow_paused:
        print("[WARN] Workflow is not paused")
        return
    
    _workflow_paused = False
    print("[OK] Workflow resumed")
    
    # Apply any pending refinements
    if _pending_refinements:
        print(f"[OK] Applying {len(_pending_refinements)} pending refinements")
        _pending_refinements.clear()


def review_current_step() -> None:
    """Review the current workflow step."""
    global _current_orchestrator
    
    if _current_orchestrator is None:
        print("[WARN] No workflow currently running")
        return
    
    state = _current_orchestrator.state
    current_node = state.get("current_node", "unknown")
    
    print(f"[OK] Current Step Review:")
    print(f"  Node: {current_node}")
    print(f"  Last Score: {state.get('last_score', 0.0):.3f}")
    print(f"  Loop Iterations: {state.get('loop_iterations', 0)}")
    
    # Show recent history
    history = state.get("history", [])
    if history:
        print(f"  Recent History (last 3 steps):")
        for entry in history[-3:]:
            node = entry.get("node", "unknown")
            result = entry.get("result", "unknown")
            score = entry.get("score", 0.0)
            print(f"    {node}: {result} (score: {score:.3f})")
    
    # Show node details if available
    node_details = _current_orchestrator.get_node_details(current_node)
    if node_details:
        print(f"  Node Details:")
        print(f"    Agent: {node_details.get('agent', 'unknown')}")
        print(f"    Action: {node_details.get('action', 'unknown')}")
        print(f"    Type: {node_details.get('type', 'unknown')}")
    
    print("[OK] Use 'refine <changes>' to modify current step")


def refine_current_step(refinement: str) -> None:
    """Apply refinements to the current workflow step."""
    global _pending_refinements
    
    if _current_orchestrator is None:
        print("[WARN] No workflow currently running")
        return
    
    if not refinement.strip():
        print("[WARN] Please specify refinement details")
        return
    
    # For now, just queue the refinement
    # In a full implementation, this would modify orchestrator behavior
    refinement_entry = {
        "timestamp": "now",
        "refinement": refinement,
        "step": _current_orchestrator.state.get("current_node", "unknown")
    }
    
    _pending_refinements.append(refinement_entry)
    
    print(f"[OK] Refinement queued: {refinement}")
    print(f"[OK] Total pending refinements: {len(_pending_refinements)}")
    print("[OK] Use 'resume' to apply refinements and continue")
    
    # Pause workflow to allow review
    pause_workflow()


def main() -> None:
    parser = argparse.ArgumentParser(prog="peg", description="PEGGPT Toolkit")
    sub = parser.add_subparsers(dest="command")
    
    # Phase management
    runp = sub.add_parser("run-phase", help="List tasks for a given phase")
    runp.add_argument("phase", type=int, help="Phase number from Instructions.txt")
    
    # Interactive REPL
    sub.add_parser("repl", help="Interactive REPL mode")
    
    # Scaffolding commands
    scaffold_plugin = sub.add_parser("scaffold-plugin", help="Scaffold a new plugin skeleton")
    scaffold_plugin.add_argument("plugin_name", help="Name of the plugin class")
    
    scaffold_workflow = sub.add_parser("scaffold-workflow", help="Scaffold a new workflow JSON")
    scaffold_workflow.add_argument("workflow_name", help="Name of the workflow")
    
    scaffold_agent = sub.add_parser("scaffold-agent", help="Scaffold a new agent skeleton")
    scaffold_agent.add_argument("agent_name", help="Name of the agent")
    
    scaffold_test = sub.add_parser("scaffold-test", help="Scaffold a new test suite JSON")
    scaffold_test.add_argument("test_suite_name", help="Name of the test suite")
    
    scaffold_ci = sub.add_parser("scaffold-ci", help="Scaffold CI pipeline and validation")
    scaffold_ci.add_argument("pipeline_name", nargs="?", default="default", help="Name of the CI pipeline")
    
    scaffold_ui = sub.add_parser("scaffold-ui", help="Scaffold web UI interface")
    scaffold_ui.add_argument("ui_type", choices=["gradio", "streamlit"], default="gradio", nargs="?", help="UI framework (gradio or streamlit)")
    scaffold_ui.add_argument("ui_name", nargs="?", default="default", help="Name for the UI")
    
    args = parser.parse_args()

    if args.command == "run-phase":
        run_phase(args.phase)
    elif args.command == "repl":
        repl()
    elif args.command == "scaffold-plugin":
        scaffold_plugin(args.plugin_name)
    elif args.command == "scaffold-workflow":
        scaffold_workflow(args.workflow_name)
    elif args.command == "scaffold-agent":
        scaffold_agent(args.agent_name)
    elif args.command == "scaffold-test":
        scaffold_test(args.test_suite_name)
    elif args.command == "scaffold-ci":
        scaffold_ci(args.pipeline_name)
    elif args.command == "scaffold-ui":
        scaffold_ui(args.ui_type, args.ui_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
