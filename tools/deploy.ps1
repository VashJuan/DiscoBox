# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

<#
.SYNOPSIS
Put the show on the board with one theme's songs & sounds.

.DESCRIPTION
1. Removes sounds on the board that the new theme doesn't use (so it fits).
2. Copies the theme's songs (those in sounds\<theme>\playlist.txt), its WAV
   chimes and the playlist to the board's \sounds\. -SongsFrom takes the songs
   and playlist from another theme (e.g. before a theme's songs are cut);
   -MaxSongs keeps only the playlist's first songs, to make room.
3. Copies the code, themes\ and lib\ (only files that changed).
4. Sets theme = "<theme>" in the board's config.py.
The board restarts by itself after the copy.

.EXAMPLE
pwsh tools\deploy.ps1 -Theme halloween
pwsh tools\deploy.ps1 -Theme generic -Drive J:
pwsh tools\deploy.ps1 -Theme halloween -SongsFrom generic -MaxSongs 26
#>
param(
    [Parameter(Mandatory)] [string] $Theme,
    [string] $Drive = "I:",
    [string] $SongsFrom = $Theme,
    [int] $MaxSongs = 0
)
$ErrorActionPreference = "Stop"

$repo = Split-Path $PSScriptRoot
$board = "$Drive\"
$themeSounds = Join-Path $repo "sounds\$Theme"
$songSounds = Join-Path $repo "sounds\$SongsFrom"
$playlistFile = Join-Path $songSounds "playlist.txt"

if (-not (Test-Path (Join-Path $board "boot_out.txt"))) {
    throw "No CircuitPython board at $Drive (no boot_out.txt). Plug it in, or give -Drive."
}
if (-not (Test-Path (Join-Path $repo "themes\$Theme.py"))) {
    throw "No theme '$Theme' (themes\$Theme.py)."
}
if (-not (Test-Path $playlistFile)) {
    throw "No $playlistFile. Cut the clips first: python tools\make_clips.py --theme $SongsFrom"
}
$songs = @(Get-Content $playlistFile | ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") })
if ($songs.Count -eq 0) { throw "$playlistFile lists no songs." }
if ($MaxSongs -gt 0) { $songs = @($songs | Select-Object -First $MaxSongs) }
$missing = @($songs | Where-Object { -not (Test-Path (Join-Path $songSounds $_)) })
if ($missing) { throw "Songs in the playlist but not in ${songSounds}: $($missing -join ', ')" }

# board name -> file on the PC
$source = [ordered]@{}
foreach ($name in $songs) { $source[$name] = Join-Path $songSounds $name }
$source["playlist.txt"] = Join-Path ([IO.Path]::GetTempPath()) "discobox-playlist.txt"
Set-Content $source["playlist.txt"] $songs
Get-ChildItem $themeSounds -Filter *.wav | ForEach-Object { $source[$_.Name] = $_.FullName }
$wanted = @($source.Keys)
$boardSounds = Join-Path $board "sounds"
New-Item -ItemType Directory -Force $boardSounds | Out-Null

if (Test-Path (Join-Path $board "code.py")) {
    Write-Warning "code.py is on the board, so it runs instead of main.py. Delete it for the show."
}

# 1. make room: remove what the new theme doesn't use
Get-ChildItem $boardSounds -File | Where-Object { $_.Name -notin $wanted } | ForEach-Object {
    Write-Host "remove sounds\$($_.Name)"
    Remove-Item $_.FullName
}

function Copy-IfChanged($from, $to) {
    $old = Get-Item $to -ErrorAction SilentlyContinue
    $new = Get-Item $from
    if ($old -and $old.Length -eq $new.Length -and
        (Get-FileHash $old).Hash -eq (Get-FileHash $new).Hash) { return }
    Write-Host "copy $($new.Name)"
    Copy-Item $from $to
}

# 2. the theme's sounds
$needKB = [int](($source.Values | ForEach-Object { (Get-Item $_).Length } |
    Measure-Object -Sum).Sum / 1KB)
$freeKB = [int]((Get-PSDrive $Drive.TrimEnd(":")).Free / 1KB)
Write-Host "Theme $Theme`: $($songs.Count) songs from $SongsFrom, $needKB KB of sounds; $freeKB KB free on the board"
foreach ($name in $wanted) {
    Copy-IfChanged $source[$name] (Join-Path $boardSounds $name)
}

# 3. code, themes & libraries
$code = "main.py", "config.py", "sensors.py", "lights.py", "prop_servo.py",
    "sound.py", "creak.py", "whistle.py"
foreach ($name in $code) { Copy-IfChanged (Join-Path $repo $name) (Join-Path $board $name) }
New-Item -ItemType Directory -Force (Join-Path $board "themes") | Out-Null
Get-ChildItem (Join-Path $repo "themes") -Filter *.py | ForEach-Object {
    Copy-IfChanged $_.FullName (Join-Path $board "themes\$($_.Name)")
}
Get-ChildItem (Join-Path $repo "lib") -Recurse -File | ForEach-Object {
    $to = Join-Path $board ($_.FullName.Substring($repo.Length + 1))
    New-Item -ItemType Directory -Force (Split-Path $to) | Out-Null
    Copy-IfChanged $_.FullName $to
}

# 4. pick the theme
$config = Join-Path $board "config.py"
$text = Get-Content $config -Raw
$text = $text -replace '(?m)^theme = ".*?"', "theme = `"$Theme`""
Set-Content $config $text -NoNewline
Write-Host "Board set to theme $Theme. Free: $([int]((Get-PSDrive $Drive.TrimEnd(':')).Free / 1KB)) KB"
