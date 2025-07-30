# PEGGPT
This repository contains configuration files and prompts for PEGGPT.

## Active Configuration

The active session configuration is stored in `SessionConfig.json`.

## Archived Configurations

Older session configuration files are stored in the `archived_configs` folder. For example, `SessionConfig_Old_4.30.json` has been moved there for reference.
=======
This repository contains prompt engineering resources and configurations.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
=======
# PEGGPT Repository

This repository contains configuration files, prompts, and workflow definitions for the **Prompt Engineering Guide (PEG)** system. PEG orchestrates prompt generation and agent coordination using a set of JSON and text assets. These files define knowledge bases, workflow graphs, session settings, and utilities for API calls.

## File Overview

| File | Purpose |
| ---- | ------- |
| `Knowledge.json` | Persistent knowledge base with facts and rules referenced by the orchestrator. |
| `Logbook.json` | Consolidated changelog and journal tracking session events and mutations. |
| `PromptEngineer.txt` | Main prompt logic describing the PEG workflow with macro definitions and export routine. |
| `PromptEngineer-v4.28.txt` | Earlier version of the prompt engineer script kept for reference. |
| `PromptModules.json` | Tool configuration for calling external APIs such as OpenAI and GitHub. |
| `SessionConfig.json` | Current session settings controlling modes, scoring, and schema links. |
| `SessionConfig_Old_4.30.json` | Previous session configuration preserved for rollback. |
| `TagEnum.json` | Standardized tag definitions used for routing, scoring, and prompt validation. |
| `Tasks.json` | Checklist items and notes used by PEG during intake and prep phases. |
| `Tests.json` | Example prompts and edge cases for validating agents and macros. |
| `WorkflowGraph.json` | Node graph describing the execution flow from intake to export. |
| `Workflows.json` | Orchestrator and agent routing definitions with revision metadata. |
| `knowledge.schematx.json` | JSON schema applied to `Knowledge.json` during validation. |

## Using the Configurations

The PEG orchestrator loads these files as part of its startup routine. Update the JSON files as needed to refine prompts, add new agents, or adjust workflows. The `SessionConfig.json` file controls which modules are enabled and links schema files for validation. `PromptModules.json` specifies API endpoints and authentication headers and is referenced whenever PEG makes external calls.

### Environment Variables

Certain operations require API credentials set as environment variables:

- `OPENAI_API_KEY` – Token for the OpenAI API used by the `openai_chat` tool.
- `GITHUB_PAT` – Personal access token used for GitHub API operations when `github_api` or `github_write` modules are enabled.

Ensure these variables are exported in your shell before running any scripts that interact with external services.

### Setup

1. Clone the repository.
2. Export the required environment variables:
   ```bash
   export OPENAI_API_KEY="<your-openai-key>"
   export GITHUB_PAT="<your-github-token>"
   ```
3. Modify the JSON configuration files to suit your workflow. `SessionConfig.json` and `PromptModules.json` are typically edited most frequently.
4. Run your PEG-based tooling or scripts. They will read from the configuration files in this directory.

This README provides a high-level overview. Review the comments within each file for additional context.

# PEGGPT

This repository contains configuration and assets for the PEG prompt engineering system, including JSON files for tasks, workflows, knowledge, and an optional `Journal.json` diary used for extended logging.

## Environment Variables

To enable GitHub API access, provide a personal access token via the `GITHUB_PAT` environment variable. The token is used by modules defined in `PromptModules.json`.

For OpenAI integration, set the `OPENAI_API_KEY` environment variable.

## Validating the Configuration

Run `validate_repo.py` before executing any agent workflows to ensure all JSON files are present and conform to `knowledge.schematx.json`. Install dependencies from `requirements.txt` first.

```bash
pip install -r requirements.txt
python validate_repo.py
```

The script exits with a non-zero status if validation fails.

## Running the Scoring Script

The repository includes a helper script `run_scoring.py` that reads a scoring model and outputs a JSON report. Use it by providing a model file and an output location:


Onboarding Guide for AI Assistants
This document outlines the core conventions and architecture of the PEG (Promptable Engineer GPT) project. Adherence to these principles is required for all development.

1. Core Philosophy
The PEG system is a "builder of tools." Its primary function is to orchestrate other agents and systems to produce high-quality, structured outputs. It operates on a principle of "evidence-based adoption," meaning all changes must be validated against tests (Tests.json) and quality metrics (PromptScoreModel.json) before being accepted.

2. Key File Conventions
WorkflowGraph.json: The single source of truth for agent orchestration. It defines the nodes (steps) and edges (transitions) of any process.

Knowledge.json: The agent's active memory. Contains facts, principles, and rules the agent must follow.

Rules.json: A subset of knowledge that defines strict, non-negotiable enforcement policies.

Logbook.json / Journal.json: The historical record. Logbook.json is for automated, machine-generated audit entries. Journal.json is for human-readable narrative and context.

/src/ directory: Contains the Python code that acts as the "brain" or execution engine for the agent.

3. Placeholder and Secret Conventions
Placeholders in Agent_Prompts.json: Prompts stored in this file use bracketed, uppercase placeholders (e.g., [DIRECTIVE_NAME]). When using one of these prompts, you must replace the placeholder with the appropriate value.

Secrets in Configuration: API keys and other secrets are never stored directly in files. They are referenced using the format <env:SECRET_NAME> (e.g., <env:OPENAI_API_KEY>). The execution environment is responsible for substituting these placeholders with actual secrets.

4. The CI/CD Pipeline (peg-ci.yml)
All commits are subject to an automated validation pipeline that:

Ensures all required files exist and are valid JSON (validate_repo.py).

Runs a suite of behavioral tests (pytest).

Scores the output against a quality model (run_scoring.py).

A commit will fail if any of these checks do not pass. Your primary goal is to ensure the CI pipeline is always passing.

```bash
python run_scoring.py --model PromptScoreModel.json --out score.json
```

The script calculates a simple average from dummy scoring values and compares it against `ci_minimum_score` defined in the model file. It exits with a non-zero status if the calculated score is below this threshold.
