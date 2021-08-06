import argparse
import json
import pathlib

from rich.progress import Progress

import stargraph


def update_all():
    args = parse_args()

    this_dir = pathlib.Path(__file__).resolve().parent
    with open(this_dir / "groups.json") as f:
        data = json.load(f)

    token = args.token_file.readline().strip() if args.token_file else None

    # merge lists
    repos = sorted(set([item for lst in data.values() for item in lst]))

    with Progress() as progress:
        task1 = progress.add_task("Total", total=len(repos))
        task2 = progress.add_task("Repo")
        for repo in repos:
            progress.update(task2, description=repo)
            nrepo = repo.replace("/", "_")
            stargraph.update_file(
                this_dir / "data" / f"{nrepo}.json",
                repo=repo,
                license="CC BY",
                creator="Nico Schlömer",
                token=token,
                progress_task=(progress, task2),
            )
            progress.advance(task1)


def parse_args():
    parser = argparse.ArgumentParser(description="Update GitHub star history files")
    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        required=True,
        help="File containing a GitHub token (can be - [stdin])",
    )
    return parser.parse_args()


if __name__ == "__main__":
    update_all()
