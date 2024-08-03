from argparse import ArgumentParser
from pathlib import Path
from dataclasses import asdict
from pprint import pprint
import sys
import pdb
import json
from datetime import datetime

from tqdm import tqdm

from joss_migrate_pmc.steps import Result, STEPS




def apply_step(step: int, repo_dir: Path('../joss-papers-pmc')) -> list[Result]:
    step_fn = STEPS[step]
    results = []
    for a_dir in tqdm(list(repo_dir.glob('joss*'))):
        res = step_fn(a_dir)
        results.append(res)
    return results


def make_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="joss_migrate_pmc")
    parser.add_argument('step', type=int, help="which step to run")
    parser.add_argument(
        '--repo', 
        type=Path, 
        help="location of joss-papers repository",
        default=Path('../joss-papers-pmc')
    )
    return parser

def save_results(results: list[Result], step: int) -> None:
    filename = f"results/step_{step}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    results_json = [asdict(r) for r in results]
    with open(filename, 'w') as f:
        json.dump(results_json, f, indent=2, default=lambda x: str(x))

def main():
    parser = make_parser()
    args = parser.parse_args()

    try:
        results = apply_step(args.step, args.repo)
    except Exception as e:
        pdb.post_mortem()
        sys.exit(1)

    errors = [r for r in results if not r.success]

    if len(errors) == 0:
        print(f"Step {args.step} applied successfully to {args.repo} :)")
        save_results(results, args.step)
        sys.exit(0)
    else:
        print(f"Error applying step {args.step} to {args.repo}:\n")
        save_results(results, args.step)
        for error in errors:
            pprint(asdict(error))
        sys.exit(1)

