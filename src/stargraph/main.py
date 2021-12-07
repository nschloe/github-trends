from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import appdirs
import numpy as np
import requests
from rich.progress import Progress


class Cache:
    def __init__(self, repo: str):
        nrepo = repo.replace("/", "_")
        self.filename = Path(appdirs.user_cache_dir()) / "stargraph" / f"{nrepo}.json"

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


def fetch_data(repos: list[str] | set[str], token: str | None = None):
    out = {}
    with Progress() as progress:
        task1 = progress.add_task("Total", total=len(repos))
        task2 = progress.add_task("Repo")
        for repo in repos:
            progress.update(task2, description=repo)
            cache = Cache(repo)

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

    c = now
    first_day_of_the_month = datetime(now.year, now.month, 1)
    while True:
        if len(old_times) > 0 and c <= old_times[-1]:
            break

        # fast-backward to next beginning of the month
        try:
            k = next(i for i, dt in enumerate(datetimes) if dt < first_day_of_the_month)
        except StopIteration:
            new_times.append(c)
            new_counts.append(len(datetimes))
            break

        new_times.append(c)
        new_counts.append(k)

        c = first_day_of_the_month
        first_day_of_the_month = _decrement_month(first_day_of_the_month)
        datetimes = datetimes[k:]

    new_times.reverse()
    new_counts.reverse()

    # cut off the last count since that represents the stars in the running month
    new_times = new_times[:-1]
    new_counts = new_counts[:-1]

    if len(old_counts) > 0:
        cs = np.cumsum(new_counts) + old_counts[-1]
        new_counts = [int(item) for item in cs]
        times = old_times + new_times
        counts = old_counts + new_counts
    else:
        times = [_decrement_month(new_times[0])] + new_times
        counts = [0] + new_counts
        counts = [int(item) for item in np.cumsum(counts)]

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
