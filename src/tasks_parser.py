"""
Parser to turn the Instructions.txt markdown into a structured list of tasks.
"""
import re
from typing import List, Dict


def parse_instructions(markdown: str) -> List[Dict[str, object]]:
    """
    Parse the Instructions.txt markdown into a list of tasks.
    Each task is represented as a dict with keys:
      - phase (int): the phase number
      - description (str): the task description
    """
    tasks: List[Dict[str, object]] = []
    current_phase: int | None = None
    for line in markdown.splitlines():
        phase_match = re.match(r"## PHASE (\d+)", line)
        if phase_match:
            current_phase = int(phase_match.group(1))
            continue

        bullet_match = re.match(r"- \[ \] (.+)", line)
        if current_phase is not None and bullet_match:
            tasks.append({
                "phase": current_phase,
                "description": bullet_match.group(1).strip(),
            })
    return tasks
