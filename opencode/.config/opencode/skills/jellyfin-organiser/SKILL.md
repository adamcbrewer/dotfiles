---
name: jellyfin-organiser
description: Organizes media files (movies and TV series) according to Jellyfin's naming conventions. Use when the user requests organizing media files, mentions Jellyfin, or needs to restructure video files into a media server format. Handles TV series with season/episode detection, fetches episode titles, and properly formats movie directories.
---

# Jellyfin Media Organizer

This skill organizes media files according to Jellyfin's official naming conventions, handling both TV series and movies with automatic metadata extraction and directory structuring.

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
   - Use `find . -type d -empty -delete` for truly empty directories
   - NEVER use wildcard patterns with `rm -rf` on directories that might contain moved files
   - Manually verify each directory is empty before removal
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
- **Safe cleanup**: Never use `rm -rf` with wildcards; only delete confirmed empty directories

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

## Special Cases

- **Multi-episode files** (S01E01E02): Retain original naming unless user requests splitting
- **Specials**: Place in "Season 00" with format `Show Name - S00E01 - Special Title.ext`
- **Ambiguous metadata**: Request user clarification for unclear show names
- **Duplicates**: Warn and ask user which file to keep
