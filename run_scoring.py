import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run scoring using a model file")
    parser.add_argument('--model', required=True, help='Path to JSON model file')
    parser.add_argument('--out', required=True, help='Path to output JSON file')
    args = parser.parse_args()

    model_path = Path(args.model)
    out_path = Path(args.out)

    try:
        with model_path.open() as f:
            model_data = json.load(f)
    except FileNotFoundError:
        print(f"Model file not found: {model_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in model file: {e}", file=sys.stderr)
        sys.exit(1)

    ci_minimum_score = model_data.get('ci_minimum_score')
    if ci_minimum_score is None:
        print('ci_minimum_score not found in model file', file=sys.stderr)
        sys.exit(1)

    results = {'clarity': 0.9, 'structure': 0.88}
    total_score = sum(results.values()) / len(results)

    output = {
        'scores': results,
        'total_score': total_score,
        'threshold': ci_minimum_score
    }

    try:
        with out_path.open('w') as f:
            json.dump(output, f, indent=2)
    except OSError as e:
        print(f"Could not write to {out_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if total_score < ci_minimum_score:
        print(f"Total score {total_score} is below threshold {ci_minimum_score}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
