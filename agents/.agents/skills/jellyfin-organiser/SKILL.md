---
name: jellyfin-organiser
description: Organizes media files (movies and TV series) according to Jellyfin's naming conventions and checks encodings for Roku and Chromecast playback compatibility. Use when the user requests organizing media files, mentions Jellyfin, or needs to restructure video files into a media server format. Handles episode titles and movie directories; probes each movie and only one episode per series.
---

# Jellyfin Media Organizer

This skill organizes media files according to Jellyfin's official naming conventions, handling both TV series and movies with automatic metadata extraction and directory structuring. It also checks encoding compatibility with Roku and Chromecast to identify likely server-side transcoding.

## Jellyfin Naming Conventions

### TV Series
```
Show Name (Year)/
  Season 01/
    Show Name - S01E01 - Episode Title.ext
    Show Name - S01E02 - Episode Title.ext
  Season 02/
    Show Name - S02E01 - Episode Title.ext
```

### Movies
```
Movie Name (Year)/
  Movie Name (Year).ext
```

## Workflow

### Discovery & Classification
Scan for video files (`.mkv`, `.mp4`, `.avi`, `.m4v`, `.mov`, `.wmv`, `.flv`, `.webm`) and classify as series or movies:
- **Series indicators**: S01E01, 1x01, season/episode patterns, multiple episodes with same base name
- **Movie indicators**: Single files, year in filename, resolution indicators without episode numbers

### Encoding & Playback Compatibility

After classification, inspect media metadata before renaming:

- **Movies**: Probe each movie file, excluding trailers and samples.
- **Series**: Probe exactly one regular episode per series across all its seasons: choose the earliest available season/episode, excluding specials, trailers and samples. Do not probe every episode or one per season. In any warning, identify the sampled filename and say that the remaining episodes are unchecked. If filenames suggest mixed releases or encodings, warn that the sample may not represent the whole series without expanding the scan.
- Use existing device details when available. Otherwise assess against the conservative shared target below and mark model-dependent results as uncertain. Ask for the Roku model and Chromecast generation only when needed for a definite verdict; continue organizing in the meantime. Casting and the native Jellyfin app on Google TV can have different support.

Use a read-only metadata probe with a quoted absolute path:

```bash
ffprobe -v error -show_format -show_streams -of json "/absolute/path/to/media.mkv"
```

Do not decode the full file or count frames. If `ffprobe` is unavailable, use `mediainfo --Output=JSON` if installed; otherwise report compatibility as unchecked and continue organizing. A failed probe is also unchecked, not proof of incompatibility.

Inspect the actual container; video codec, profile, level, pixel format/bit depth, resolution, frame rate, bitrate and HDR metadata; audio codec/profile, channels and sample rate; and subtitle formats. Ignore cover-art streams. For H.264, ffprobe's level `41` means 4.1 and `50` means 5.0; other codecs use different level scales. Missing metadata remains unknown.

**Assess Roku and Chromecast separately:**

- **Likely compatible**: Within the known device limits, or the conservative shared target when models are unknown. This is a metadata assessment, not a playback guarantee.
- **Potential transcoding / model-dependent**: Outside the shared target or dependent on the device, Jellyfin client, selected tracks or audio receiver. Name the exact property causing concern.
- **Incompatible with direct play**: A documented limit for the known model/client is exceeded. Explain whether remuxing, audio conversion or video transcoding is likely; Jellyfin may still play it by converting it.
- **Unchecked**: Metadata could not be obtained.

**Conservative shared target**: MP4, H.264 Baseline/Main/High up to Level 4.1, 8-bit `yuv420p`, SDR, up to 1080p30 (or 720p60), and AAC-LC stereo. This is a broadly compatible encoding recommendation, not an exhaustive support list or a universal bitrate limit.

**Compatibility rules:**

- Chromecast 1st/2nd generation supports H.264 up to High Level 4.1 at 1080p30 or 720p60; 3rd generation and Ultra support up to 4.2 at 1080p60. H.264 Level 5.0 therefore exceeds these devices' documented limits even for a 1080p file. Newer Google TV models have different limits; consult the exact model's documentation.
- Roku support varies by model and firmware. Flag H.264 above 4.1 for verification when the model is unknown, rather than declaring it incompatible with every Roku.
- HEVC, VP9, AV1, 4K, HDR, H.264 High 10, and 4:2:2/4:4:4 video require model/profile-specific checks. HEVC is unsupported on classic Chromecast generations 1–3, but supported on Ultra and appropriate Google TV devices. HEVC support on Roku is associated with 4K-capable models; do not assume every Roku supports it.
- Distinguish AAC-LC from HE-AAC. HE-AAC is not universally incompatible: Google Cast explicitly supports it. Flag uncertainty only where the device/client profile warrants it. Multi-channel AAC, AC-3, E-AC-3, DTS and TrueHD need checks against the device and connected TV/receiver; passthrough support is not the same as decoding support.
- Consider default audio/subtitle tracks and compatible alternatives. An unsupported optional track does not force transcoding unless selected. PGS/VobSub or styled ASS subtitles may require burn-in and therefore video transcoding when enabled; text subtitles may be converted separately.
- A container mismatch alone may need only remuxing (copying the encoded streams). MKV is not inherently bad: Roku supports it, while the Cast receiver may need a different container. Audio-only conversion is different from expensive video re-encoding.
- Bitrate/network limits, playback quality settings and Jellyfin client profiles can still trigger transcoding for compatible codecs. If playback evidence is available, prefer Jellyfin's actual transcode reason over a metadata guess. Client-side audio decoding does not itself mean server-side transcoding.

Keep compatibility output warning-only. If a file appears compatible, say nothing about its encoding. For confirmed incompatibility, potential issues or an unchecked probe, give a short warning naming the movie/series, affected device and reason, then tell the user to test playback on that device. For series, include the sampled episode and note that the rest are unchecked. Do not include a compatibility table, routine passing results or unsolicited conversion recommendations. Example: **Warning:** `Film.mp4` uses H.264 Level 5.0, above older Chromecast limits. Test playback on your Chromecast and check whether Jellyfin transcodes.

If the user later asks for a fix, suggest the smallest necessary change: select a compatible track, remux, convert audio only, or re-encode video to the shared target. Run conversion only if the user requests it. Renaming extensions or merely changing a declared codec level does not fix an incompatible encoding.

**References** (consult for model-specific verdicts):
- [Google Cast supported media](https://developers.google.com/cast/docs/media)
- [Roku supported media and audio](https://support.roku.com/article/208754908) — describes Roku Media Player/device capabilities; Jellyfin's client profile can differ.

### TV Series Processing

Extract metadata from filenames (show name, year, season, episode) by cleaning dots, removing release group tags like `[eztv.re]`, `[RARBG]`, and quality indicators like `.1080p`, `.BluRay`.

**Episode titles**: Search for official episode names using queries like "[Show Name] season [X] episode list". Use parallel/background searches for multiple seasons when possible. If unavailable, proceed with format: `Show Name - S01E01.ext`

**Structure**: Create `Show Name (Year)/Season XX/` directories and move files with format: `Show Name - S01E01 - Episode Title.ext`, preserving extensions and official capitalization.

### Movie Processing

Extract movie name and year from filenames, cleaning quality indicators and release groups. Search for missing years or verify spelling when needed.

**Structure**: Create `Movie Name (Year)/` directory and move file with format: `Movie Name (Year).ext`

### Cleanup

**CRITICAL SAFETY PROTOCOL:**
1. **NEVER use destructive cleanup commands until ALL moves are verified**
2. **Create a verification checkpoint** after moving files:
   - Count source files before moving
   - Count destination files after moving
   - Verify counts match exactly
   - List and verify each moved file exists in new location
3. **Only remove directories that are confirmed empty** using safe methods:
   - Build an explicit list of absolute source directories involved in this run
   - Show that list to the user before cleanup
   - Use `rmdir -- "$source_directory"` for each listed directory, one at a time
   - Never discover cleanup targets recursively or use `.` as the cleanup root
   - NEVER use wildcard patterns with `rm -rf` on directories that might contain moved files
   - Verify each exact directory is empty before removal
4. **Two-phase cleanup approach**:
   - Phase 1: Move all files and verify success
   - Phase 2: Only after verification, remove confirmed empty source directories one by one
5. **If any verification fails**: Stop immediately, report to user, do not proceed with cleanup

## Best Practices

- **Verify before moving**: Confirm source files exist before operations
- **Filename cleaning**: Remove release tags, quality indicators (1080p, BluRay, etc.), replace dots/underscores with spaces
- **Year handling**: Required for movies; include for series when disambiguating (e.g., "The Office (US)")
- **Batch processing**: Group by series/season or all movies together
- **Error handling**: Organize with available data even if episode titles can't be found
- **User confirmation**: Ask for clarification on ambiguous show names or years
- **Web sources**: Prefer official sources (IMDb, TheTVDB, Wikipedia) for metadata
- **Directory creation**: Create all directories before moving files to prevent errors
- **Verification checkpoints**: Always verify file operations succeeded before cleanup
- **Safe cleanup**: Delete only explicit, absolute source paths confirmed empty during this run

## Example

Input: `Show.Name.S01E01.1080p.mkv`
1. Detect series pattern (S01E01)
2. Parse: Show="Show Name", Season=01, Episode=01
3. Search "Show Name season 1 episode list" for titles
4. Create `Show Name/Season 01/`
5. Move to `Show Name/Season 01/Show Name - S01E01 - Pilot.mkv`
6. **VERIFY** the file exists at new location
7. **VERIFY** source directory is empty
8. Only then remove empty source directory

## Output Summary

Provide summary with:
- Files processed count
- Series/seasons and movies organized
- Final directory structure
- Unprocessed files with reasons
- Compatibility warnings only for incompatible, potentially problematic or unchecked media: identify the affected device, briefly explain why, and ask the user to test playback
- Within series warnings, name the sampled episode and state **one episode sampled; remaining episodes unchecked**, including any mixed-release caveat
- Omit compatibility output entirely when no issues are identified

## Special Cases

- **Multi-episode files** (S01E01E02): Retain original naming unless user requests splitting
- **Specials**: Place in "Season 00" with format `Show Name - S00E01 - Special Title.ext`
- **Ambiguous metadata**: Request user clarification for unclear show names
- **Duplicates**: Warn and ask user which file to keep
