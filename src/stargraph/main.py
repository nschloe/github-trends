import base64
import json
import pathlib
from datetime import datetime
from typing import Optional

import numpy as np
import requests


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


def get_time(repo: str, k: int, token: Optional[str], api: str = "v3"):
    assert k >= 1
    headers = {}
    if token is not None:
        headers["Authorization"] = f"token {token}"

    if api == "v3":
        url = f"https://api.github.com/repos/{repo}/stargazers"
        # Send those headers to get starred_at
        headers["Accept"] = "application/vnd.github.v3.star+json"
        r = requests.get(url, headers=headers, params={"page": k, "per_page": 1})
        assert (
            r.ok
        ), f"{r.url}, status code {r.status_code}, {r.reason}, {r.json()['message']}"
        time_str = r.json()[0]["starred_at"]
    else:
        # graphql
        assert api == "v4"
        url = "https://api.github.com/graphql"
        owner, name = repo.split("/")
        # construct the cursor according to
        # <https://stackoverflow.com/a/64140209/353337>
        # TODO unfortunately, this doesn't always work; keep an eye on
        # <https://github.com/isaacs/github/issues/1958>
        # <https://github.community/t/get-stargazer-time-with-custom-cursor/171929>
        cursor = base64.b64encode(f"cursor:{k}".encode()).decode()
        query = f"""
        {{
          repository(owner: "{owner}", name: "{name}") {{
            stargazers (last: 1, before: "{cursor}") {{
              edges {{
               starredAt
              }}
            }}
          }}
        }}
        """
        r = requests.post(url, headers=headers, json={"query": query})
        assert (
            r.ok
        ), f"{r.url}, status code {r.status_code}, {r.reason}, {r.json()['message']}"
        time_str = r.json()["data"]["repository"]["stargazers"]["edges"][0]["starredAt"]

    # https://stackoverflow.com/a/969324/353337
    date_fmt = "%Y-%m-%dT%H:%M:%S%z"
    time = datetime.strptime(time_str, date_fmt)
    # remove timezone information
    time = time.replace(tzinfo=None)
    return time


def update_github_star_data(data, repo, token):
    last_known_datetime = None
    # last_known_datetime = datetime(2008, 11, 1)

    owner, name = repo.split("/")
    selection = "last: 100"

    now = datetime.utcnow().replace(microsecond=0)

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
