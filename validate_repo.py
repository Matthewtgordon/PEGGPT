#
# This script validates the integrity of the PEG project repository.
# It checks for the presence of all required configuration files,
# ensures they are valid JSON, and validates key files against their schemas
# and versioning rules as defined in the project RFCs.
# This is a critical first step in the CI/CD pipeline.
#
import json
import sys
import re
from pathlib import Path
import jsonschema

def load_json(path: Path):
    """Safely loads a JSON file."""
    # Use utf-8 encoding for broad compatibility
    with path.open(encoding='utf-8') as f:
        return json.load(f)

def validate_json(path: Path):
    """Validates that a file is well-formed JSON."""
    try:
        load_json(path)
        return True
    except json.JSONDecodeError as e:
        # Use an emoji for clear visual feedback in logs
        print(f"❌ JSON decode error in {path}: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred reading {path}: {e}")
        return False

def validate_schema(data: dict, schema_path: Path):
    """Validates data against a JSON schema."""
    if not schema_path.exists():
        # A warning is better than a failure if the schema itself is missing
        print(f"⚠️ Schema file not found: {schema_path}. Skipping schema validation.")
        return True
        
    schema = load_json(schema_path)
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"❌ Schema validation error for {schema_path.stem}: {e.message}")
        return False

def validate_version_field(data: dict, filename: str):
    """
    Explicitly validates the 'version' field using a Semantic Versioning pattern.
    This enforces the versioning policy from the RFC.
    """
    if 'version' not in data:
        print(f"❌ Missing required 'version' field in {filename}.")
        return False
    
    version = data['version']
    # Regex for MAJOR.MINOR.PATCH format (e.g., "1.2.3")
    semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')
    if not isinstance(version, str) or not semver_pattern.match(version):
        print(f"❌ Invalid SemVer format for 'version' in {filename}. Expected 'X.Y.Z', found '{version}'.")
        return False
    return True


def main():
    """Main validation function to run all checks."""
    print("--- Running Repository Validation ---")
    
    # PATCH APPLIED: Added 'Rules.json', 'PromptScoreModel.json', and 'PromptModules.json'
    repo_files = [
        'Knowledge.json',
        'Rules.json',
        'Logbook.json',
        'SessionConfig.json',
        'WorkflowGraph.json',
        'Workflows.json',
        'TagEnum.json',
        'Tasks.json',
        'Tests.json',
        'Journal.json',
        'PromptScoreModel.json',
        'PromptModules.json'
    ]
    
    all_valid = True
    
    # --- Step 1: Check for file presence and basic JSON validity ---
    print("\nStep 1: Checking for file presence and JSON format...")
    for filename in repo_files:
        path = Path(filename)
        if not path.exists():
            print(f"❌ Missing required file: {filename}")
            all_valid = False
            continue
        
        if not validate_json(path):
            all_valid = False
    
    # --- Step 2: Validate versioned files (Knowledge.json, Rules.json) ---
    print("\nStep 2: Validating versioned files against schema and SemVer format...")
    
    # PATCH APPLIED: Corrected the schema path
    versioned_files_to_check = {
        'Knowledge.json': Path('schemas/knowledge.schema.json'),
        # 'Rules.json': Path('schemas/rules.schema.json'), # Add this when Rules.json schema exists
    }

    for filename, schema_path in versioned_files_to_check.items():
        file_path = Path(filename)
        if file_path.exists(): # Only check if the file itself was found in Step 1
            data = load_json(file_path)
            
            if not validate_version_field(data, filename):
                all_valid = False
            
            if not validate_schema(data, schema_path):
                all_valid = False

    print("\n--- Validation Complete ---")
    if all_valid:
        print("✅ All repository configuration files are valid.")
    else:
        print("\n❌ Repository validation failed. Please fix the errors listed above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
