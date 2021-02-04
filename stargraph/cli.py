import argparse
import sys
from datetime import timedelta
from pathlib import Path

from matplotlib import pyplot as plt

from .__about__ import __version__
from .main import update_file
from .tools import plot


def main(argv=None):
    args = parse_args(argv)

    # get the data
    filenames = []
    token = args.token_file.readline().strip() if args.token_file else None
    for repo in args.repos:
        p = Path(".") if args.cache_dir is None else Path(args.cache_dir)
        filenames.append(p / ("github-" + repo.replace("/", "_") + ".json"))
        update_file(
            filenames[-1],
            timedelta(days=args.max_gap_days),
            repo=repo,
            token=token,
            title="GitHub stars",
            verbose=True,
        )

    if args.font is not None:
        plt.rc("font", family=args.font)

    # plot it
    plot(filenames)
    plt.title("Star count on GitHub")
    if args.output:
        plt.savefig(args.output, transparent=True, bbox_inches="tight")
    else:
        plt.show()


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="GitHub star history",
        # Needed for line break in --version:
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("repos", nargs="+", type=str, help="repositories to analyze")

    parser.add_argument(
        "-m",
        "--max-gap-days",
        required=True,
        type=int,
        help="Maximum number of days between two measurements",
    )

    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        help="File containing a GitHub token (can be - [stdin])",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output image file (optional, default: show plot)",
    )

    parser.add_argument(
        "-d",
        "--cache-dir",
        type=str,
        help="Cache directory (optional, default: current directory)",
    )

    parser.add_argument(
        "-f",
        "--font",
        type=str,
        help="Which font to use (optional, default: default matplotlib font)",
    )

    version = "\n".join(
        [
            "stargraph {} [Python {}.{}.{}]".format(
                __version__,
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            "Copyright (C) 2020 Nico Schlömer <nico.schloemer@gmail.com>",
        ]
    )

    parser.add_argument(
        "--version",
        "-v",
        help="display version information",
        action="version",
        version=version,
    )
    return parser.parse_args(argv)
