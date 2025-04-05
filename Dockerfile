# Run the docker container ([with]/without CUDA-enabled GPUs):
#   `docker run [--gpus all ]-it --rm quest-generation`

FROM mambaorg/micromamba:git-fddee42-cuda12.2.2-ubuntu20.04

WORKDIR /app

USER root

# Copy the environment configuration file and install dependencies
COPY environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Copy the pip dependency requirements file, install curl,
# and install uv for resolving pip dependencies
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH=/opt/conda/bin:/root/.local/bin:$PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv pip install --python=/opt/conda/bin/python --upgrade pip && \
    uv pip install --python=/opt/conda/bin/python -r requirements.txt

# Switch to the default user, copy all project files,
# and give access to the working directory to the user
USER mambauser
COPY . .

# Activate the conda environment
ARG MAMBA_DOCKERFILE_ACTIVATE=1

CMD [ "bash" ]
