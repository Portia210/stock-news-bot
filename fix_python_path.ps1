# Get the current PATH
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')

# Python paths to add
$pythonPath = "C:\Users\hp\AppData\Local\Programs\Python\Python312"
$scriptsPath = "C:\Users\hp\AppData\Local\Programs\Python\Python312\Scripts"

# Remove WindowsApps Python if it exists
$windowsAppsPath = "C:\Users\hp\AppData\Local\Microsoft\WindowsApps"
$paths = $currentPath.Split(';') | Where-Object { $_ -ne $windowsAppsPath -and $_ -ne "" }

# Add Python paths if they don't exist
if ($paths -notcontains $pythonPath) {
    $paths = @($pythonPath) + $paths
}
if ($paths -notcontains $scriptsPath) {
    $paths = @($scriptsPath) + $paths
}

# Join paths back together
$newPath = $paths -join ';'

# Set the new PATH
[Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')

Write-Host "Python paths have been added to system PATH."
Write-Host "Please restart your terminal for changes to take effect." 