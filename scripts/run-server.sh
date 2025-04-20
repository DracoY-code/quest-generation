#!/bin/bash

SERVICE_NAME="${1:-jupyterlab}"

set -e  # Exit immediately on error

# Move to the .devcontainer directory
cd .devcontainer || {
    echo "Failed to enter .devcontainer directory";
    exit 1;
}

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "docker-compose.yml not found in $(pwd)"
    exit 1
fi

# Run the container with service ports and clean up after exit
if [ ! docker compose run --rm --service-ports --remove-orphans -i "$SERVICE_NAME" ]; then
    echo "Failed to run service '$SERVICE_NAME'"
    exit 1
fi

# Move back to the root directory
cd ..
