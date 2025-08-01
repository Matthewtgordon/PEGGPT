# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This directory contains three main projects:

### 1. claude-desktop-debian/
A build system for creating Linux (.deb and .AppImage) packages of Claude Desktop from the Windows installer. This is an Electron application packaging project.

### 2. peggpt/PEGGPT/
A sophisticated prompt engineering system called PEG (Prompt Engineering Guide) that orchestrates AI agents through JSON configuration files and Python execution scripts.

### 3. peg_runtime/
An alternative/runtime variant of the PEGGPT system with similar configuration files.

## Common Development Commands

### Claude Desktop Debian
```bash
cd claude-desktop-debian
# Build .deb package (default)
./build.sh

# Build AppImage
./build.sh --build appimage --clean no

# Build with specific cleanup behavior
./build.sh --build deb --clean yes
```

### PEGGPT System
```bash
cd peggpt/PEGGPT
# Install dependencies
pip install -r requirements.txt

# Validate all configuration files
python validate_repo.py

# Run scoring system
python run_scoring.py --model PromptScoreModel.json --out score.json

# Run tests
pytest

# Set up environment variables
export OPENAI_API_KEY="your-key-here"
export GITHUB_PAT="your-token-here"
```

### PEG Runtime
```bash
cd peg_runtime
# Install dependencies
pip install jsonschema

# Validate configuration
python validate_repo.py
```

## Architecture Overview

### Claude Desktop Debian
- **build.sh**: Main build orchestrator with architecture detection
- **scripts/**: Contains build-deb-package.sh and build-appimage.sh
- **package.json**: Defines electron/asar dependency for unpacking Windows installer
- Workflow: Downloads Windows installer → Extracts resources → Replaces native modules → Repackages for Linux

### PEGGPT System Architecture
The PEG system is a sophisticated agent orchestration framework with the following key components:

#### Core Configuration Files
- **WorkflowGraph.json**: Defines execution flow as nodes and edges (single source of truth)
- **Knowledge.json**: Persistent knowledge base with facts and rules
- **Rules.json**: Strict enforcement policies (subset of knowledge)
- **SessionConfig.json**: Current session settings and schema links
- **PromptModules.json**: API connectors for external services (OpenAI, GitHub)
- **Modules.json**: Available macros and tool definitions

#### Python Execution Engine (/src/)
- **orchestrator.py**: Core "brain" - graph execution engine that brings WorkflowGraph.json to life
- **bandit_selector.py**: Intelligent macro selection system
- **loop_guard.py**: Prevents infinite loops in agent execution
- **knowledge_update.py**: Updates knowledge base dynamically

#### Validation and Quality Control
- **validate_repo.py**: Ensures all JSON files conform to schemas
- **run_scoring.py**: Quality scoring against PromptScoreModel.json
- **Tests.json**: Example prompts and edge cases for validation
- **schemas/**: JSON schema definitions for validation

#### Key Conventions
- Placeholders in prompts use `[UPPERCASE_NAME]` format
- Secrets use `<env:SECRET_NAME>` format (never stored directly)
- All changes must pass CI validation pipeline
- Logbook.json for machine logs, Journal.json for human narrative

## Environment Variables

### PEGGPT Projects
- `OPENAI_API_KEY`: Required for OpenAI API integration
- `GITHUB_PAT`: Required for GitHub API operations

## Testing and Validation

### PEGGPT System
The system includes comprehensive validation:
1. **validate_repo.py**: Structural integrity checks
2. **pytest**: Behavioral test suite
3. **run_scoring.py**: Quality scoring against model
4. All must pass for CI success

### Claude Desktop Debian
- Build process includes automatic dependency checking
- Validates architecture compatibility (amd64/arm64)
- Tests package integrity during build

## File Dependencies Map (PEGGPT)

```
WorkflowGraph.json → reads Modules.json → reads PromptModules.json
       ↓
src/orchestrator.py → reads SessionConfig.json
       ↓                    ↓
bandit_selector.py    Knowledge.json/Rules.json
loop_guard.py              ↓
       ↓              knowledge_update.py
run_scoring.py
```

## Development Notes

- The claude-desktop-debian project requires Debian-based systems
- PEGGPT system uses "evidence-based adoption" - all changes must be validated
- Never run build scripts as root user
- PEGGPT CI pipeline enforces quality gates on all commits
- Configuration files are the primary interface - Python scripts execute the configurations