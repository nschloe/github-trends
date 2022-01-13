import json
import os
from pathlib import Path

from _main import fetch_data, plot

try:
    token = os.environ["GH_ACCESS_TOKEN"]
except KeyError:
    # fall back to file
    with open(Path.home() / ".github-access-token") as f:
        token = f.read().strip()

this_dir = Path(__file__).resolve().parent

with open(this_dir / "groups.json") as f:
    data = json.load(f)


all_repos = {repo for item in data.values() for repo in item}

repo_data = fetch_data(all_repos, token=token, cache_dir=this_dir / ".." / ".cache")

plot_dir = this_dir / ".." / "plots"
plot_dir.mkdir(exist_ok=True)

for group_name, repos in data.items():
    plt = plot({repo: repo_data[repo] for repo in repos})

    xlim = plt.gca().get_xlim()
    ylim = plt.gca().get_ylim()
    plt.text(
        xlim[0],
        -(ylim[1] - ylim[0]) * 0.1,
        "@nschloe / gh-trends | Nico Schlömer | CC BY",
        fontsize="x-small",
        verticalalignment="top",
    )
    plt.savefig(plot_dir / f"{group_name}.svg", bbox_inches="tight", transparent=True)
    # plt.show()
    plt.close()
