#!/bin/bash
set -e  # Exit immediately on error

# Move to the .devcontainer directory
cd .devcontainer || { echo "Failed to enter .devcontainer directory"; exit 1; }

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "docker-compose.yml not found in $(pwd)"
    exit 1
fi

# Run the container with service ports and clean up after exit
docker compose run --rm --service-ports --remove-orphans app
