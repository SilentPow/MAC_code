@echo off
setlocal enabledelayedexpansion

rem Directory containing .mp4 files
set "input_dir=.\MAC_web\full_videos\normal"
rem Directory to store HLS output
set "output_dir=.\MAC_web\videos\normal"

rem Ensure the output directory exists
if not exist "%output_dir%" mkdir "%output_dir%"

rem Loop through all .mp4 files in the input directory
for %%f in ("%input_dir%\*.mp4") do (
    set "filename=%%~nf"
    echo Converting %%f to HLS...

    ffmpeg -i "%%f" -codec: copy -start_number 0 -hls_time 1 -hls_list_size 0 -hls_segment_type fmp4 -hls_flags independent_segments -hls_playlist_type vod -sc_threshold 0 "%output_dir%\!filename!.m3u8"

    if %errorlevel% neq 0 (
        echo Failed to convert %%f
    ) else (
        echo Successfully converted %%f to HLS format.
    )
)

echo Conversion completed.
pause
