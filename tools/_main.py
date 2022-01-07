from __future__ import annotations

import json
from datetime import datetime
from itertools import accumulate
from pathlib import Path

import matplotx
import requests
from matplotlib import pyplot as plt
from rich.progress import Progress


class Cache:
    def __init__(self, repo: str, cache_dir: Path | None):
        if cache_dir is None:
            import appdirs

            cache_dir = Path(appdirs.user_cache_dir()) / "gh-trends"

        cache_dir.mkdir(parents=True, exist_ok=True)
        nrepo = repo.replace("/", "_")
        self.filename = cache_dir / f"{nrepo}.json"

    def read(self) -> dict:
        if not self.filename.is_file():
            return {}
        try:
            with open(self.filename) as f:
                content = json.load(f)
        except Exception:
            return {}
        return {datetime.fromisoformat(key): value for key, value in content.items()}

    def write(self, data: dict[datetime, int]):
        with open(self.filename, "w") as f:
            json.dump(
                {key.isoformat(): value for key, value in data.items()},
                f,
                indent=2,
                ensure_ascii=False,
            )


def fetch_data(repos: list[str] | set[str], token: str, cache_dir: Path | None) -> dict:
    out = {}
    with Progress() as progress:
        task1 = progress.add_task("Total", total=len(repos))
        task2 = progress.add_task("Repo")
        for repo in repos:
            progress.update(task2, description=repo)
            cache = Cache(repo, cache_dir)

            data = cache.read()
            data = _update(data, repo, token, progress_task=(progress, task2))
            cache.write(data)

            out[repo] = data
            progress.advance(task1)
    return out


def _update(data, repo, token, progress_task):
    old_times = list(data.keys())
    old_counts = list(data.values())

    now = datetime.utcnow().replace(microsecond=0)

    if len(old_times) > 0 and old_times[-1] == datetime(now.year, now.month, 1):
        return data

    owner, name = repo.split("/")

    progress, task = progress_task

    total_count = _get_num_remaining_api_calls(owner, name, token)
    last_counts = 0 if len(old_counts) == 0 else old_counts[-1]
    num = -(-(total_count - last_counts) // 100)
    if progress is not None:
        progress.update(task, description=repo, total=num, completed=0)

    selection = "last: 100"

    datetimes = []
    while True:
        query = f"""
        {{
          repository(owner:"{owner}", name:"{name}") {{
            stargazers({selection}) {{
              pageInfo {{
                hasPreviousPage
                startCursor
              }}
              edges {{
                starredAt
              }}
            }}
          }}
        }}
        """

        res = requests.post(
            "https://api.github.com/graphql",
            json={"query": query},
            headers={"Authorization": f"token {token}"},
        )
        assert res.ok

        data = res.json()["data"]["repository"]["stargazers"]
        batch = [
            datetime.fromisoformat(item["starredAt"].replace("Z", ""))
            for item in data["edges"]
        ]
        batch.reverse()
        datetimes += batch

        first_in_list = data["edges"][0]["starredAt"]
        first_in_list = datetime.fromisoformat(first_in_list.replace("Z", ""))

        if progress is not None:
            progress.advance(task)

        if not data["pageInfo"]["hasPreviousPage"]:
            break

        cursor = data["pageInfo"]["startCursor"]
        selection = f'last: 100, before: "{cursor}"'

        if len(old_times) > 0 and first_in_list < old_times[-1]:
            break

    new_times = []
    new_counts = []

    # fast-backward to the beginning of the month
    c = datetime(now.year, now.month, 1)
    try:
        k = next(i for i, dt in enumerate(datetimes) if dt < c)
    except StopIteration:
        datetimes = []
    else:
        datetimes = datetimes[k:]

    while True:
        if len(datetimes) == 0 or (len(old_times) > 0 and c <= old_times[-1]):
            new_times.append(c)
            new_counts.append(0)
            break

        new_times.append(c)
        c = _decrement_month(c)
        # fast-backward to next beginning of the month
        try:
            k = next(i for i, dt in enumerate(datetimes) if dt < c)
        except StopIteration:
            new_counts.append(len(datetimes))
            datetimes = []
        else:
            new_counts.append(k)
            datetimes = datetimes[k:]

    assert len(new_times) == len(new_counts)

    new_times.reverse()
    new_counts.reverse()

    times = old_times[:-1] + new_times
    # cumsum:
    cs = list(accumulate(new_counts))
    n = len(cs)
    if len(old_counts) > 0:
        for k in range(n):
            cs[k] += old_counts[-1][k]
    new_counts = [int(item) for item in cs]
    counts = [old_counts[:-1][k] + new_counts[k] for k in range(n)]

    return dict(zip(times, counts))


def _get_num_remaining_api_calls(owner, name, token):
    # find total
    query = f"""
    {{
      repository(owner:"{owner}", name:"{name}") {{
        stargazers {{
          totalCount
        }}
      }}
    }}
    """
    headers = {"Authorization": f"token {token}"}
    res = requests.post(
        "https://api.github.com/graphql", json={"query": query}, headers=headers
    )
    assert res.ok

    res = res.json()
    if "errors" in res:
        raise RuntimeError(res["errors"][0]["message"])
    return res["data"]["repository"]["stargazers"]["totalCount"]


def _decrement_month(dt):
    month = (dt.month - 2) % 12 + 1
    year = dt.year - month // 12
    return datetime(year, month, 1)


plt.style.use(matplotx.styles.duftify(matplotx.styles.tab20r))


# https://stackoverflow.com/a/3382369/353337
def _argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def plot(data, sort: bool = True, cut: float | None = None, max_num: int = 20):
    # convert data dict to list of tuples
    data = list(data.items())

    if sort:
        # sort them such that the largest at the last time step gets plotted first and
        # the colors are in a nice order
        last_vals = [list(vals.values())[-1] for _, vals in data]
        data = [data[i] for i in _argsort(last_vals)[::-1]]

    if cut is not None:
        # cut those files where the max data is less than cut*max_overall
        max_vals = [max(list(vals.values())) for _, vals in data]
        max_overall = max(max_vals)
        data = [
            content
            for content, max_val in zip(data, max_vals)
            if max_val > cut * max_overall
        ]

    if max_num is not None:
        # show only max_num repos
        data = data[:max_num]

    n = len(data)
    for k, (repo, values) in enumerate(data):
        times = list(values.keys())
        values = list(values.values())
        plt.plot(times, values, label=repo, zorder=n - k)

    matplotx.line_labels()
    matplotx.ylabel_top("GitHub stars")
    return plt
