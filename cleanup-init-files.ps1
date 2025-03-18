$directories = Get-ChildItem -Recurse -Directory | Select-Object -ExpandProperty FullName
$dupes = @()

foreach ($dir in $directories) {
    $initFiles = Get-ChildItem -Path $dir -Filter "__init__.py" -File | Sort-Object -Property LastWriteTime -Descending
    if ($initFiles.Count -gt 1) {
        $dupes += [PSCustomObject]@{
            Directory = $dir
            Count = $initFiles.Count
            MostRecent = $initFiles[0].FullName
            Duplicates = $initFiles | Select-Object -Skip 1 | ForEach-Object { $_.FullName }
        }
    }
}

if ($dupes.Count -gt 0) {
    Write-Host "Found directories with duplicate __init__.py files:"
    foreach ($dupe in $dupes) {
        Write-Host "`nDirectory: $($dupe.Directory)"
        Write-Host "Contains $($dupe.Count) __init__.py files"
        Write-Host "Most recent file: $($dupe.MostRecent)"
        Write-Host "Older duplicates:"
        foreach ($dup in $dupe.Duplicates) {
            Write-Host "  - $dup"
        }
    }

    $confirmation = Read-Host "Do you want to delete the older duplicate __init__.py files? (y/n)"
    if ($confirmation -eq 'y') {
        foreach ($dupe in $dupes) {
            foreach ($dup in $dupe.Duplicates) {
                Write-Host "Deleting: $dup"
                Remove-Item -Path $dup -Force
            }
        }
        Write-Host "Cleanup completed!"
    } else {
        Write-Host "No files were deleted."
    }
} else {
    Write-Host "No directories with duplicate __init__.py files found."
}