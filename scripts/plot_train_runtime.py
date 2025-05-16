from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import Colormap
from matplotlib.container import BarContainer


# Set the default plot style
sns.set_style("whitegrid")
sns.set_palette("colorblind")

plt.rc("font", size=14, family="sans-serif", **{"sans-serif": ["Helvetica"]})
plt.rc("axes", labelsize=16, titlesize=18, titlepad=14, labelpad=12)
plt.rc("legend", fontsize=14)
plt.rc("xtick", labelsize=14)
plt.rc("ytick", labelsize=14)

# Set the constants for the directories and figures
WORKING_DIR: Final[str] = str(Path().resolve())
LOGGING_DIR: Final[str] = str(Path(WORKING_DIR) / "logs")
IMAGE_DIR: Final[str] = str(Path(WORKING_DIR) / "images")
FIGURE_WIDTH: Final[float] = 7.0
FIGURE_HEIGHT: Final[float] = 5.0
BAR_HEIGHT: Final[float] = 0.2


def read_train_runtime(
    logging_dir: PathLike = LOGGING_DIR, filename: str = "train_runtime.json"
) -> pd.DataFrame:
    filepath: Path = Path(logging_dir) / filename
    if not filepath.exists():
        raise FileNotFoundError(f"'{filepath}' does not exist.")

    with open(filepath, "r") as json_reader:
        train_runtime: dict[str, float] = {
            model_key: round(results[-1]["value"], 2)
            for model_key, results in dict(json.load(json_reader)).items()
        }

    return pd.DataFrame.from_dict(
        train_runtime, orient="index", columns=["runtime"]
    ).reset_index(names="model_key")


def format_seconds(seconds: float) -> str:
    hrs: int = int(seconds // 3600)
    mins: int = int((seconds % 3600) // 60)
    secs: int = int(seconds % 60)

    return f"{hrs:02}:{mins:02}:{secs:02}"


def make_runtime_barplot(
    runtime_data: dict[str, dict[int, str]],
    name: str = "train_runtime",
    format: str = "png",
    dpi: int = 300,
    image_dir: PathLike = IMAGE_DIR,
    tight_layout: bool = True,
    figsize: tuple[float, float] = (FIGURE_WIDTH, FIGURE_HEIGHT),
) -> None:
    model_keys: list[str] = list(runtime_data["model_key"].values())
    runtimes: list[float] = list(runtime_data["runtime"].values())
    log_runtimes: list[float] = np.log10(runtimes)
    colormap: Colormap = plt.get_cmap("Pastel1")(range(len(model_keys)))
    x_offset: float = (max(log_runtimes) - min(log_runtimes)) * 0.03

    plt.figure(figsize=figsize)
    bars: BarContainer = plt.barh(
        model_keys,
        log_runtimes,
        color=colormap,
        edgecolor="black",
    )

    for bar, log_runtime, runtime in zip(bars, log_runtimes, runtimes):
        formatted_time: str = format_seconds(runtime)
        plt.text(
            log_runtime + x_offset,
            bar.get_y() + bar.get_height() / 2,
            formatted_time,
            va="center",
            fontsize=14,
            color="black",
        )

    plt.xlim(0, max(log_runtimes) + x_offset * 15)
    plt.xlabel(r"Training Runtime (in log$_{10}$ seconds)")
    plt.title("Training Runtime per Model")
    plt.yticks(range(len(model_keys)))
    if tight_layout:
        plt.tight_layout()

    Path(image_dir).mkdir(parents=True, exist_ok=True)
    filepath: str = str(Path(image_dir) / f"{name}.{format}")

    plt.savefig(filepath, dpi=dpi, format=format)
    print(f"Saved to '{filepath}'")
    plt.close()


if __name__ == "__main__":
    runtime_df: pd.DataFrame = read_train_runtime()
    print(f"Train Runtime Data:\n\n{runtime_df}\n")
    make_runtime_barplot(runtime_df.to_dict())
