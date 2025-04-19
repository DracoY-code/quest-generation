# PowerShell script: run-server.ps1

$ErrorActionPreference = "Stop"  # Exit on error

# Move to the .devcontainer directory
Set-Location -Path ".devcontainer"

# Check if docker-compose.yml exists
if (-Not (Test-Path "docker-compose.yml")) {
    Write-Error "docker-compose.yml not found in $($PWD.Path)"
    exit 1
}

# Run the container with service ports and clean up after exit
docker compose run --rm --service-ports --remove-orphans app

# Move back to the root directory
Set-Location ..
