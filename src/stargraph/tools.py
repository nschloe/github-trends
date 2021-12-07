from __future__ import annotations

import matplotx
from matplotlib import pyplot as plt


def _merge(a, b):
    return {**a, **b}


plt.style.use(_merge(matplotx.styles.tab20r, matplotx.styles.dufte))


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
