import json
import pathlib
from datetime import datetime

import mplx
from matplotlib import pyplot as plt


def _merge(a, b):
    return {**a, **b}


plt.style.use(_merge(mplx.styles.tab20r, mplx.styles.dufte))


# https://stackoverflow.com/a/3382369/353337
def _argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def show(*args, **kwargs):
    plot(*args, **kwargs)
    plt.show()


def plot(filenames, sort=True, cut=None, max_num=20):
    # read data
    data = []
    for filename in filenames:
        with open(filename) as f:
            data.append(json.load(f))

    if sort:
        # sort them such that the largest at the last time step gets plotted first and
        # the colors are in a nice order
        last_vals = [list(content["data"].values())[-1] for content in data]
        data = [data[i] for i in _argsort(last_vals)[::-1]]

    if cut is not None:
        # cut those files where the max data is less than cut*max_overall
        max_vals = [max(list(content["data"].values())) for content in data]
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
    for k, content in enumerate(data):
        data = content["data"]
        data = {datetime.fromisoformat(key): value for key, value in data.items()}

        times = list(data.keys())
        values = list(data.values())
        label = content["name"]

        plt.plot(times, values, label=label, zorder=n - k)

    mplx.line_labels()

    if "creator" in content:
        _add_license_statement(content)


def _get_avg_per_day(times, values):
    return [
        (values[k + 1] - values[k])
        / ((times[k + 1] - times[k]).total_seconds() / 3600 / 24)
        for k in range(len(values) - 1)
    ]


def _get_middle_times(lst):
    return [
        datetime.fromtimestamp(
            (datetime.timestamp(lst[k]) + datetime.timestamp(lst[k + 1])) / 2
        )
        for k in range(len(lst) - 1)
    ]


def plot_per_day(filenames, sort=True, cut=None):
    if sort:
        # sort them such that the largest at the last time step gets plotted first and
        # the colors are in a nice order
        last_vals = []
        for filename in filenames:
            with open(filename) as f:
                content = json.load(f)
            vals = list(content["data"].values())
            last_vals.append(vals[-1] - vals[-2])

        filenames = [filenames[i] for i in _argsort(last_vals)[::-1]]

    if cut is not None:
        # cut those files where the max data is less than cut*max_overall
        max_vals = []
        for filename in filenames:
            with open(filename) as f:
                content = json.load(f)
            vals = list(content["data"].values())
            vals = [vals[k + 1] - vals[k] for k in range(len(vals) - 1)]
            max_vals.append(max(vals))

        max_overall = max(max_vals)
        filenames = [
            filename
            for filename, max_val in zip(filenames, max_vals)
            if max_val > cut * max_overall
        ]

    times = []
    values = []
    labels = []
    for filename in filenames:
        filename = pathlib.Path(filename)
        assert filename.is_file(), f"{filename} not found."

        with open(filename) as f:
            content = json.load(f)

        data = content["data"]
        data = {datetime.fromisoformat(key): value for key, value in data.items()}

        t = list(data.keys())
        v = list(data.values())
        times.append(_get_middle_times(t))
        values.append(_get_avg_per_day(t, v))
        labels.append(content["name"])

    # start plotting from the 0 before the first value
    for j, (tm, val) in enumerate(zip(times, values)):
        for i, x in enumerate(val):
            if x > 0:
                k = max(i - 1, 0)
                break
        times[j] = tm[k:]
        values[j] = val[k:]

    n = len(times)
    for k, (time, vals, label) in enumerate(zip(times, values, labels)):
        plt.plot(time, vals, label=label, zorder=n - k)

    mplx.line_labels()

    if "creator" in content:
        _add_license_statement(content)


def _add_license_statement(content):
    creator = content["creator"]
    license = content["license"]
    data_source = content["data source"]
    xlim = plt.gca().get_xlim()
    ylim = plt.gca().get_ylim()
    plt.text(
        xlim[0],
        -(ylim[1] - ylim[0]) * 0.1,
        f"{data_source} | {creator} | {license}",
        fontsize="x-small",
        verticalalignment="top",
    )
