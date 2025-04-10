import matplotlib.pyplot as plt


def init_styles() -> None:
    """Sets the default `matplotlib` plot styles."""

    plt.rc("font", size=12, family="sans-serif", **{"sans-serif": ["Helvetica"]})
    plt.rc("axes", labelsize=12, titlesize=12, titlepad=8, labelpad=6)
    plt.rc("legend", fontsize=10)
    plt.rc("xtick", labelsize=8)
    plt.rc("ytick", labelsize=8)
