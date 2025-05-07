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

        # Separate out metrics
        grouped_metrics: list[str] = ["bleu", "meteor", "bertscore"]

        # Plot perplexity separately
        perplexities = [self.data[m].get("perplexity", 0.0) for m in model_names]
        _, ax = plt.subplots(figsize=figsize)
        colormap = plt.get_cmap("Pastel1")(range(len(model_names)))

        ax.barh(
            range(len(model_names)),
            perplexities,
            color=colormap,
            edgecolor="black",
        )
        ax.set_xlabel("Perplexity")
        ax.set_yticks(range(len(model_names)))
        ax.set_yticklabels(model_names)
        ax.set_title("Perplexity per Model")

        self.save_plot_to_image_dir(
            name=f"{name}_perplexity",
            format=format,
            dpi=dpi,
            image_dir=image_dir,
            tight_layout=tight_layout,
        )

        # Plot BLEU, METEOR, BERTScore together
        values_dict: dict[str, list[float]] = {metric: [] for metric in grouped_metrics}
        for model in model_names:
            for metric in grouped_metrics:
                if metric == "bertscore":
                    values_dict[metric].append(
                        self.data[model].get(metric, {}).get("f1", 0.0)
                    )
                else:
                    values_dict[metric].append(self.data[model].get(metric, 0.0))

        _, ax = plt.subplots(figsize=figsize)
        num_metrics: int = len(grouped_metrics)
        bar_width: float = BAR_HEIGHT
        indices: list[int] = range(len(model_names))
        colormap: Colormap = plt.get_cmap("Pastel2")(range(num_metrics))

        for i, metric in enumerate(grouped_metrics):
            ax.barh(
                [index + (i - num_metrics // 2) * bar_width for index in indices],
                values_dict[metric],
                height=bar_width,
                color=colormap[i],
                edgecolor="black",
                label=(metric.title() if metric != "bertscore" else "BERTScore F1"),
            )

        ax.set_xlabel("Score")
        ax.set_yticks(indices)
        ax.set_yticklabels(model_names)
        ax.set_title("BLEU, METEOR, BERTScore per Model")
        ax.legend()

        self.save_plot_to_image_dir(
            name=f"{name}_text_metrics",
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
