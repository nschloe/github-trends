import argparse
import sys
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt

from ..__about__ import __version__
from ..github import update_file
from ..tools import plot


def star_history(argv=None):
    args = parse_args(argv)

    # get the data
    filenames = []
    for repo in args.repos:
        p = Path(".") if args.cache_dir is None else Path(args.cache_dir)
        filenames.append(p / ("github-" + repo.replace("/", "_") + ".json"))
        update_file(
            filenames[-1],
            timedelta(days=args.max_gap_days),
            repo=repo,
            token=args.token,
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
        help="maximum number of days between two measurements",
    )

    parser.add_argument("-t", "--token", type=str, help="GitHub token")

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
            "hotware {} [Python {}.{}.{}]".format(
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
