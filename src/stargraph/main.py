import json
import pathlib
from datetime import datetime

import numpy as np
import requests
from rich.progress import Progress


def update_file(
    filename,
    repo=None,
    token=None,
    title="GitHub stars",
    creator=None,
    license=None,
    verbose=False,
):
    filename = pathlib.Path(filename)
    if filename.is_file():
        with open(filename) as f:
            content = json.load(f)

        if repo is not None:
            assert content["name"] == repo
        if title is not None:
            assert content["title"] == title
        if creator is not None:
            assert content["creator"] == creator
        if license is not None:
            assert content["license"] == license

        data = content["data"]
    else:
        data = {}
        assert repo is not None

    data = {datetime.fromisoformat(key): value for key, value in data.items()}

    data = update_github_star_data(data, repo, token, verbose=verbose)

    d = {}
    if title is not None:
        d["title"] = title
    d["name"] = repo
    if creator is not None:
        d["creator"] = creator
    if license is not None:
        d["license"] = license
    d["data source"] = "GitHub API via stargraph"
    now = datetime.utcnow()
    now = now.replace(microsecond=0)
    d["last updated"] = now.isoformat()

    d["data"] = dict(zip([t.isoformat() for t in data.keys()], data.values()))

    with open(filename, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def get_total_count(owner, name, token):
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
    return res.json()["data"]["repository"]["stargazers"]["totalCount"]


def update_github_star_data(data, repo, token, verbose=False):
    last_known_datetime = None
    last_known_count = 0

    owner, name = repo.split("/")

    total_count = get_total_count(owner, name, token)
    num_api_calls = -(-(total_count - last_known_count) // 100)

    selection = "last: 100"

    now = datetime.utcnow().replace(microsecond=0)

    with Progress() as progress:
        task = progress.add_task(repo, total=num_api_calls)

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

            headers = {"Authorization": f"token {token}"}

            res = requests.post(
                "https://api.github.com/graphql", json={"query": query}, headers=headers
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

            progress.advance(task)

            if not data["pageInfo"]["hasPreviousPage"]:
                break

            cursor = data["pageInfo"]["startCursor"]
            selection = f'last: 100, before: "{cursor}"'

            if last_known_datetime is not None and first_in_list < last_known_datetime:
                break

    times = []
    counts = []

    c = datetime(datetimes[0].year, datetimes[0].month, 1)
    while len(datetimes) > 0:
        # fast-backward to next beginning of the month
        try:
            k = next(i for i, dt in enumerate(datetimes) if dt < c)
        except StopIteration:
            times.append(c)
            counts.append(len(datetimes))
            break

        times.append(c)
        counts.append(k)

        c = decrement_month(c)
        if last_known_datetime is not None and c <= last_known_datetime:
            break
        datetimes = datetimes[k:]

    times.reverse()
    counts.reverse()

    times = times + [now]
    counts = [0] + counts

    counts = [int(item) for item in np.cumsum(counts)]

    return dict(zip(times, counts))


def decrement_month(dt):
    month = (dt.month - 2) % 12 + 1
    year = dt.year - month // 12
    return datetime(year, month, 1)
