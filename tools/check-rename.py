"""
Check if repos have been renamed/moved.
"""
import json
from pathlib import Path

import requests
from rich import print
from rich.progress import track

this_dir = Path(__file__).parents[0]

with open(this_dir / "groups.json") as f:
    data = json.load(f)


all_repos = {repo for item in data.values() for repo in item}

for repo in track(all_repos, description="Checking..."):
    res = requests.get(f"https://github.com/{repo}", allow_redirects=False)
    if res.status_code != 200:
        if "Location" in res.headers:
            print(f"[red]{repo} {res.status_code} -> {res.headers['Location']}[/]")
        else:
            print(f"[red]{repo} {res.status_code}[/]")
