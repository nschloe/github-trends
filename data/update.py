import argparse
import json
import pathlib
from datetime import timedelta
from rich.progress import Progress

import stargraph


def _string_fixed_length(string, length):
    if len(string) > length:
        return string[:length]
    return string.rjust(length)



def update_groups():
    args = parse_args()

    this_dir = pathlib.Path(__file__).resolve().parent
    with open(this_dir / "groups.json") as f:
        data = json.load(f)

    token = args.token_file.readline().strip() if args.token_file else None

    with Progress() as progress:
        task1 = progress.add_task("group", total=len(data))
        task2 = progress.add_task("repos", total=0)
        for group_name, repos in data.items():
            progress.update(task1, description=_string_fixed_length(group_name, 20))
            progress.update(task2, total=len(repos), completed=0)
            for repo in repos:
                progress.update(task2, description=_string_fixed_length(repo, 20))
                stargraph.update_file(
                    this_dir / "data" / "{}.json".format(repo.replace("/", "_")),
                    max_interval_length=timedelta(days=30),
                    repo=repo,
                    license="CC BY",
                    creator="Nico Schlömer",
                    token=token,
                )
                progress.advance(task2)
            progress.advance(task1)


def parse_args():
    parser = argparse.ArgumentParser(description="Update GitHub star history files")
    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        help="File containing a GitHub token (can be - [stdin])",
    )
    return parser.parse_args()


if __name__ == "__main__":
    update_groups()
