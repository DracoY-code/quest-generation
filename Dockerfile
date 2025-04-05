FROM mambaorg/micromamba:git-fddee42-cuda12.2.2-ubuntu20.04

WORKDIR /app

# Set environment variables
ENV MAMBA_ROOT_PREFIX=/opt/micromamba \
    PATH=/opt/micromamba/bin:$PATH

# Copy the environment configuration file and install dependencies
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n questgen -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Activate the new conda environment
ENV CONDA_DEFAULT_ENV=questgen
ENV PATH=/opt/micromamba/envs/questgen/bin:$PATH
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Copy the requirements file and install uv for pip dependency installation
COPY requirements.txt .
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv pip install --upgrade pip && \
    uv pip install -r requirements.txt

COPY . .

CMD [ "bash" ]
