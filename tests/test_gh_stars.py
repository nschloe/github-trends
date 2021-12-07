import os

import stargraph


def test_stargraph():
    token = os.environ["GH_ACCESS_TOKEN"]
    data = stargraph.fetch_data(["nschloe/stargraph"], token)
    plt = stargraph.plot(data)
    plt.show()
