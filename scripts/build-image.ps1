# PowerShell script: build-image.ps1

$ErrorActionPreference = "Stop"  # Exit on error

$startTime = Get-Date

# Auto-detect the host architecture
$arch = (Get-CimInstance Win32_Processor).Architecture

switch ($arch) {
    9 {  # x86_64
        $env:TARGET_PLATFORM = "amd64"
        $env:DOCKER_PLATFORM = "linux/amd64"
    }
    12 {  # arm64 | aarch64
        $env:TARGET_PLATFORM = "arm64"
        $env:DOCKER_PLATFORM = "linux/arm64"
    }
    Default {
        Write-Error "Unsupported architecture: $arch"
        exit 1
    }
}

# Save the environment variables
$envFile = ".\.env"
@"
TARGET_PLATFORM=$($env:TARGET_PLATFORM)
DOCKER_PLATFORM=$($env:DOCKER_PLATFORM)
"@ | Set-Content -Path $envFile

# Output the build information (for debug)
Write-Host "Detected platform: $($env:DOCKER_PLATFORM)"
Write-Host "Building image: (questgen:$($env:TARGET_PLATFORM))"

# Build the Docker image for the platform
# and load it into the local Docker
docker buildx build `
    --platform $env:DOCKER_PLATFORM `
    --tag questgen:$($env:TARGET_PLATFORM) `
    --output type=docker .

$endTime = Get-Date
$elapsed = $endTime - $startTime

Write-Host "`nBuild completed for $($env:DOCKER_PLATFORM) in $($elapsed.TotalSeconds)s"
