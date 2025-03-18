# Get the current PATH variable
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Split the PATH into individual entries
$pathEntries = $currentPath -split ";"

# Fix each entry
$fixedEntries = @()
foreach ($entry in $pathEntries) {
    $trimmedEntry = $entry.Trim()
    # Skip empty entries
    if ($trimmedEntry -eq "") {
        continue
    }
    # Remove any existing quotes
    $unquotedEntry = $trimmedEntry -replace '^"(.*)"$', '$1'
    # Add quotes if the path has spaces
    if ($unquotedEntry -match '\s') {
        $fixedEntries += "`"$unquotedEntry`""
    } else {
        $fixedEntries += $unquotedEntry
    }
}

# Join the entries back together
$newPath = $fixedEntries -join ";"

# Output the current and new paths for comparison
Write-Host "Current PATH: $currentPath"
Write-Host "New PATH: $newPath"

# Confirm before making changes
$confirmation = Read-Host "Apply these changes? (y/n)"
if ($confirmation -eq 'y') {
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "PATH variable updated successfully."
} else {
    Write-Host "No changes were made."
}