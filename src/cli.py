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
        print(f"❌ Instructions.txt not found in {file_path.resolve().parent}")
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
            print("Commands:\n  run-phase <n>\n  scaffold plugin <PluginName>\n  exit / quit")
            continue
        if intent == "run_phase":
            run_phase(params["phase"])
            continue
        if intent == "scaffold_plugin":
            scaffold_plugin(params["plugin_name"])
            continue
        print("❓ Unknown command. Type 'help'.")


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
    print(f"✔️ Scaffolded plugin: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="peg", description="PEGGPT Toolkit")
    sub = parser.add_subparsers(dest="command")
    runp = sub.add_parser("run-phase", help="List tasks for a given phase")
    runp.add_argument("phase", type=int, help="Phase number from Instructions.txt")
    sub.add_parser("repl", help="Interactive REPL mode")
    scaffold = sub.add_parser("scaffold-plugin", help="Scaffold a new plugin skeleton")
    scaffold.add_argument("plugin_name", help="Name of the plugin class")
    args = parser.parse_args()

    if args.command == "run-phase":
        run_phase(args.phase)
    elif args.command == "repl":
        repl()
    elif args.command == "scaffold-plugin":
        scaffold_plugin(args.plugin_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
