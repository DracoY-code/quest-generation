#!/bin/bash
set -e  # Exit immediately on error

start_time=$(date +%s)

# Auto-detect the host architecture
ARCH=$(uname -m)

if [[ "$ARCH" == "x86_64" ]]; then
    export TARGET_PLATFORM=amd64
    export DOCKER_PLATFORM=linux/amd64
elif [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
    export TARGET_PLATFORM=arm64
    export DOCKER_PLATFORM=linux/arm64
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Save the environment variables
ENV_FILE=".devcontainer/.env"
echo "TARGET_PLATFORM=$TARGET_PLATFORM" > $ENV_FILE
echo "DOCKER_PLATFORM=$DOCKER_PLATFORM" >> $ENV_FILE
echo "HUGGINGFACE_HUB_TOKEN=$HUGGINGFACE_HUB_TOKEN" >> $ENV_FILE

# Output the build information (for debug)
echo "Detected platform: $DOCKER_PLATFORM"
echo "Building image: (questgen:$TARGET_PLATFORM)"
if [ -n "$HUGGINGFACE_HUB_TOKEN" ]; then
    echo "Access token: set"
else
    echo "Access token: not set"
fi

# Build the Docker image for the platform
# and load it into the local Docker
DOCKER_FILE=".devcontainer/Dockerfile"
docker buildx build \
    -f $DOCKER_FILE \
    --platform $DOCKER_PLATFORM \
    --tag questgen:$TARGET_PLATFORM \
    --output type=docker .

end_time=$(date +%s)
elapsed=$(( end_time - start_time ))

echo
echo "Build completed for $DOCKER_PLATFORM in ${elapsed}s."
