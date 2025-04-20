# Save the docker image into a TAR file:
#   `docker save -o <filename>.tar <image-name>[:<tag>]`
# 
# Zip the image TAR file using `gzip`:
#   `gzip <filename>.tar`
# 
# Unzip and load the compressed TAR file using `gunzip`:
#   `gunzip -c <filename>.tar.gz | docker load`
# 
# Run the docker container ([with]/without CUDA-enabled GPUs):
#   `docker run [--gpus all ]-v ".:/app" -it --rm questgen:${TARGET_PLATFORM}`

FROM mambaorg/micromamba:2-cuda12.4.1-ubuntu20.04

WORKDIR /app

USER root

# Install build-essential to get a C compiler
RUN apt-get update && apt-get install -y build-essential

# Copy the environment configuration file and install dependencies
COPY .devcontainer/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Copy the pip dependency requirements file and install them
COPY .devcontainer/requirements.txt /tmp/requirements.txt

ENV PATH=/opt/conda/bin:/root/.local/bin:$PATH
RUN /opt/conda/bin/python -m pip install --upgrade pip && \
    /opt/conda/bin/python -m pip install -r /tmp/requirements.txt && \
    /opt/conda/bin/python -m pip cache purge

# Switch to the default user, copy all project files,
# and give access to the working directory to the user
USER mambauser
COPY . .

# Activate the conda environment
ARG MAMBA_DOCKERFILE_ACTIVATE=1

CMD [ "bash" ]
