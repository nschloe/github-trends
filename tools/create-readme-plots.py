import json
from pathlib import Path

import stargraph

with open(Path.home() / ".github-access-token") as f:
    token = f.read().strip()

this_dir = Path(__file__).parents[0]

with open(this_dir / "groups.json") as f:
    data = json.load(f)


all_repos = {repo for item in data.values() for repo in item}

repo_data = stargraph.fetch_data(all_repos, token=token)

for group_name, repos in data.items():
    plt = stargraph.plot({repo: repo_data[repo] for repo in repos})

    xlim = plt.gca().get_xlim()
    ylim = plt.gca().get_ylim()
    plt.text(
        xlim[0],
        -(ylim[1] - ylim[0]) * 0.1,
        "@nschloe / stargraph | Nico Schlömer | CC BY",
        fontsize="x-small",
        verticalalignment="top",
    )
    plt.savefig(f"{group_name}.svg", bbox_inches="tight", transparent=True)
    # plt.show()
    plt.close()
