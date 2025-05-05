from __future__ import annotations

import json
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import Any, Final, Literal

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.lines import Line2D


# Set the default plot style
sns.set_style("whitegrid")

plt.rc("font", size=12, family="serif", **{"serif": ["Times", "Times New Roman"]})
plt.rc("axes", labelsize=12, titlesize=12, titlepad=10, labelpad=8)
plt.rc("legend", fontsize=11)
plt.rc("xtick", labelsize=10)
plt.rc("ytick", labelsize=10)

# Set the constants for the directories and figures
WORKING_DIR: Final[str] = str(Path().resolve())
OUTPUT_DIR: Final[str] = str(Path(WORKING_DIR) / "out")
IMAGE_DIR: Final[str] = str(Path(WORKING_DIR) / "images")
METRIC_TYPES: Final[set[str]] = {"training", "generation"}
FIGURE_WIDTH: Final[float] = 7.0
FIGURE_HEIGHT: Final[float] = 3.2
BAR_HEIGHT: Final[float] = 0.1


class Metric(ABC):
    def __init__(self, type: str, data: dict[str, dict[str, Any]]):
        self.type: str = type
        self.data: dict[str, dict[str, Any]] = data

    @classmethod
    @abstractmethod
    def load(
        cls,
        type: Literal["training", "generation"],
        output_dir: PathLike = OUTPUT_DIR,
    ) -> Metric:
        if type not in METRIC_TYPES:
            raise ValueError("`type` must be one of: 'training', 'generation'.")

        filepath: Path = Path(output_dir) / f"{type}_metrics.json"
        if not filepath.exists():
            raise FileNotFoundError(f"'{filepath}' does not exist.")

        with open(filepath, "r", encoding="utf-8") as fileptr:
            data: dict[str, Any] = json.load(fileptr)
        print(f"[LOAD] {filepath / type}_metrics.json")

        return cls(type, data)

    @abstractmethod
    def plot(
        self,
        name: str,
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = IMAGE_DIR,
        tight_layout: bool = True,
        figsize: tuple[float, float] = (FIGURE_WIDTH, FIGURE_HEIGHT),
    ) -> None: ...

    @abstractmethod
    def save_plot_to_image_dir(
        self,
        *,
        name: str,
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = OUTPUT_DIR,
        tight_layout: bool = True,
    ) -> None:
        if tight_layout:
            plt.tight_layout()

        Path(image_dir).mkdir(parents=True, exist_ok=True)
        filepath: str = str(Path(image_dir) / f"{name}.{format}")

        plt.savefig(filepath, dpi=dpi, format=format)
        print(f"[SAVE] {filepath}")
        plt.close()


class TrainingMetrics(Metric):
    @classmethod
    def load(cls, output_dir: PathLike = OUTPUT_DIR):
        return super().load("training", output_dir)

    def plot(
        self,
        name: str = "training",
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = IMAGE_DIR,
        tight_layout: bool = True,
        figsize: tuple[float, float] = (FIGURE_WIDTH, FIGURE_HEIGHT),
    ) -> None:
        ax: Axes
        metrics: set[str] = {"train_losses", "learning_rates"}

        for metric in metrics:
            _, ax = plt.subplots(figsize=figsize)
            metric_name: str = metric.replace("_", " ").title()

            for label, data in self.data.items():
                epochs: list[int] = data.get(
                    "epochs", list(range(len(data.get(metric, []))))
                )
                lines: list[Line2D] = ax.plot(
                    epochs, data.get(metric, []), label=label, marker="o"
                )

                if metric == "train_losses":
                    eval_losses: list[float] = data.get("eval_losses", [])
                    ax.plot(
                        [epochs[-1]],
                        [eval_losses[0]],
                        marker="x",
                        color=lines[0].get_color(),
                        label=f"{label} (eval_loss)",
                    )

                ax.set_xlabel("Epochs")
                ax.set_ylabel(metric_name)
                ax.legend()

            self.save_plot_to_image_dir(
                name=f"{name}_{metric}",
                format=format,
                dpi=dpi,
                image_dir=image_dir,
                tight_layout=tight_layout,
            )

    def save_plot_to_image_dir(
        self,
        *,
        name: str = "training",
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = OUTPUT_DIR,
        tight_layout: bool = True,
    ):
        return super().save_plot_to_image_dir(
            name=name,
            format=format,
            dpi=dpi,
            image_dir=image_dir,
            tight_layout=tight_layout,
        )


class GenerationMetrics(Metric):
    @classmethod
    def load(cls, output_dir: PathLike = OUTPUT_DIR):
        return super().load("generation", output_dir)

    def plot(
        self,
        name: str = "generation",
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = IMAGE_DIR,
        tight_layout: bool = True,
        figsize: tuple[float, float] = (FIGURE_WIDTH, FIGURE_HEIGHT),
    ) -> None:
        ax: Axes
        model_names: list[str] = list(self.data.keys())
        n: int = len(model_names)
        metrics: set[str] = {"perplexity", "bleu", "meteor", "bertscore"}

        for metric in metrics:
            _, ax = plt.subplots(figsize=figsize)

            values: list[float]
            if metric == "bertscore":
                values = [
                    self.data[m].get(metric, {}).get("f1", 0.0) for m in model_names
                ]
            else:
                values = [self.data[m].get(metric, 0.0) for m in model_names]

            colormap: Colormap = plt.get_cmap("Pastel1")(range(n))
            ax.barh(
                range(n),
                values,
                height=BAR_HEIGHT,
                color=colormap,
                edgecolor="black",
            )
            ax.set_xlabel(
                metric.title()
                if metric == "perplexity"
                else "BERTScore F1"
                if metric == "bertscore"
                else metric.upper()
            )
            ax.set_yticks(range(n))
            ax.set_yticklabels(model_names)

            self.save_plot_to_image_dir(
                name=f"{name}_{metric}",
                format=format,
                dpi=dpi,
                image_dir=image_dir,
                tight_layout=tight_layout,
            )

    def save_plot_to_image_dir(
        self,
        *,
        name: str = "generation",
        format: str = "png",
        dpi: int = 300,
        image_dir: PathLike = OUTPUT_DIR,
        tight_layout: bool = True,
    ):
        return super().save_plot_to_image_dir(
            name=name,
            format=format,
            dpi=dpi,
            image_dir=image_dir,
            tight_layout=tight_layout,
        )


if __name__ == "__main__":
    # Load the metrics data: 'training' and 'generation'
    training_metrics: TrainingMetrics = TrainingMetrics.load()
    generation_metrics: GenerationMetrics = GenerationMetrics.load()

    # Create the plots and save them to the `IMAGE_DIR`
    training_metrics.plot()
    generation_metrics.plot()
