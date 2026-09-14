#!/usr/bin/env bash
set -euo pipefail

version="7.6.6"
archive="$RUNNER_TEMP/powershell-$version-linux-x64.tar.gz"
destination="$RUNNER_TEMP/powershell-$version"
expected="ddbc4a2d113bbd46d283cfedcbcd117a70caefd7673f41f2b4e0000badf103bc"

curl --fail --silent --show-error --location \
  "https://github.com/PowerShell/PowerShell/releases/download/v$version/powershell-$version-linux-x64.tar.gz" \
  --output "$archive"
printf '%s  %s\n' "$expected" "$archive" | sha256sum --check --strict
mkdir "$destination"
tar --extract --gzip --file "$archive" --directory "$destination"
chmod +x "$destination/pwsh"
printf '%s\n' "$destination" >> "$GITHUB_PATH"
