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
from matplotlib.container import BarContainer


# Set the default plot style
sns.set_style("whitegrid")
sns.set_palette("colorblind")

plt.rc("font", size=16, family="sans-serif", **{"sans-serif": ["Helvetica"]})
plt.rc("axes", labelsize=18, titlesize=20, titlepad=16, labelpad=14)
plt.rc("legend", fontsize=14)
plt.rc("xtick", labelsize=14)
plt.rc("ytick", labelsize=14)

# Set the constants for the directories and figures
WORKING_DIR: Final[str] = str(Path().resolve())
OUTPUT_DIR: Final[str] = str(Path(WORKING_DIR) / "out")
IMAGE_DIR: Final[str] = str(Path(WORKING_DIR) / "images")
METRIC_TYPES: Final[set[str]] = {"training", "generation"}
FIGURE_WIDTH: Final[float] = 7.0
FIGURE_HEIGHT: Final[float] = 5.0
BAR_HEIGHT: Final[float] = 0.2


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
        metric_map: dict[str, str] = {
            "train_losses": "Training Loss",
            "grad_norms": "Gradient Norms",
        }

        for metric, ylabel in metric_map.items():
            _, ax = plt.subplots(figsize=figsize)

            for model_name, model_data in self.data.items():
                values: list[float] = model_data.get(metric, [])
                if not values:
                    continue

                # Infer x-axis (epochs) if not explicitly provided
                epochs: list[int] = model_data.get("epochs", list(range(len(values))))

                if len(epochs) > len(values):
                    epochs = epochs[: len(values)]

                # Plot each line with consistent formatting
                ax.plot(epochs, values, marker="o", label=model_name)

            ax.set_xlabel("Epochs")
            ax.set_ylabel(ylabel)
            ax.set_title(f"{ylabel} over Epochs")
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
        all_metrics: list[str] = ["Perplexity", "BLEU", "METEOR", "BERTScore"]
        indices: list[int] = range(len(model_names))
        colormap: Colormap = plt.get_cmap("Pastel1")(indices)

        # Acquire the values for each metric in lists
        values_dict: dict[str, list[float]] = {metric: [] for metric in all_metrics}
        for model in model_names:
            for metric in all_metrics:
                if metric == "BERTScore":
                    values_dict[metric].append(
                        self.data[model].get(metric.lower(), {}).get("f1", 0.0)
                    )
                else:
                    values_dict[metric].append(
                        self.data[model].get(metric.lower(), 0.0)
                    )

        # Make the plots for each metric
        for i, metric in enumerate(all_metrics):
            _, ax = plt.subplots(figsize=figsize)
            bars: BarContainer = ax.barh(
                indices,
                values_dict[metric],
                color=colormap,
                edgecolor="black",
            )

            metric_name: str = metric if metric != "BERTScore" else "BERTScore F1"
            ax.set_xlabel(metric_name)
            ax.set_yticks(indices)
            ax.set_yticklabels(model_names)
            ax.set_title(f"{metric_name} per Model")

            x_min: float = min(values_dict[metric])
            x_max: float = max(values_dict[metric])
            x_offset: float = (x_max - x_min) / 5
            ax.set_xlim(x_min - x_offset, x_max + x_offset)

            for bar, metric_value in zip(bars, values_dict[metric]):
                plt.text(
                    metric_value + x_offset / 10,
                    bar.get_y() + bar.get_height() / 2,
                    f"{metric_value:.3f}",
                    va="center",
                    fontsize=14,
                    color="black",
                )

            self.save_plot_to_image_dir(
                name=f"{name}_{metric.lower()}",
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
