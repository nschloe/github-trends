import argparse
import json
import pathlib
from datetime import timedelta

import stargraph


def update_groups():
    args = parse_args()

    this_dir = pathlib.Path(__file__).resolve().parent
    with open(this_dir / "groups.json") as f:
        data = json.load(f)

    token = args.token_file.readline().strip() if args.token_file else None

    for group in data.values():
        print()
        for repo in group:
            print(repo, "...")
            stargraph.update_file(
                this_dir / "data" / "{}.json".format(repo.replace("/", "_")),
                max_interval_length=timedelta(days=30),
                repo=repo,
                license="CC BY",
                creator="Nico Schlömer",
                token=token,
            )


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
