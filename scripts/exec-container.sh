#!/bin/bash
set -e  # Exit immediately on error

# Move to the .devcontainer directory
cd .devcontainer || { echo "Failed to enter .devcontainer directory"; exit 1; }

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "docker-compose.yml not found in $(pwd)"
    exit 1
fi

# Run the container and start an interactive bash terminal
docker compose exec app bash
