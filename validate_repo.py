import json
import sys
from pathlib import Path
import jsonschema

def load_json(path: Path):
    with path.open() as f:
        return json.load(f)

def validate_json(path: Path):
    try:
        load_json(path)
        return True
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {path}: {e}")
        return False

def validate_schema(data: dict, schema_path: Path):
    with schema_path.open() as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Schema validation error in {schema_path}: {e.message}")
        return False

def main():
    repo_files = [
        'Knowledge.json',
        'Logbook.json',
        'SessionConfig.json',
        'WorkflowGraph.json',
        'Workflows.json',
        'TagEnum.json',
        'Tasks.json',
        'Tests.json',
        'Journal.json'
    ]
    all_valid = True
    for filename in repo_files:
        path = Path(filename)
        if not path.exists():
            print(f"Missing required file: {filename}")
            all_valid = False
            continue
        if not validate_json(path):
            all_valid = False
    # Validate Knowledge.json against schema if schema present
    k_schema = Path('knowledge.schematx.json')
    if k_schema.exists():
        data = load_json(Path('Knowledge.json'))
        if not validate_schema(data, k_schema):
            all_valid = False
    if all_valid:
        print("All configuration files are valid.")
    else:
        print("Configuration validation failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
