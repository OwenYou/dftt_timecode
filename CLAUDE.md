# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- **Recommended:** Use `uv` package manager (used in CI/CD)
  - Install dependencies: `uv sync`
  - Run commands with dependencies: `uv run <command>`
- **Alternative:** Traditional pip
  - Install in development mode: `pip install -e .`
  - Install dev dependencies: `pip install -e .[dev]` (requires pyproject.toml dependency groups)

### Testing
- Run all tests: `pytest` or `uv run pytest`
- Run with verbose output: `pytest -v -s` (configured in pyproject.toml)
- Run specific test file: `pytest test/test_dftt_timecode.py`
- Run specific test for TimeRange: `pytest test/test_dftt_timerange.py`

### Documentation
- Build docs: `cd docs && make html` or `cd docs && uv run make html`
- Clean build: `cd docs && make clean`
- View docs: Open `docs/_build/html/index.html`
- **Note:** Documentation uses Sphinx with MyST-Parser for Markdown support

### Building and Publishing
- Build package: `uv build`
- Publishing is automated via GitHub Actions on release creation

## Code Structure

This is a Python timecode library for the film and TV industry with high frame rate support.

### Package Organization
```
dftt_timecode/
├── core/
│   ├── dftt_timecode.py    # Core DfttTimecode class
│   └── dftt_timerange.py   # DfttTimeRange class for time intervals
├── pattern.py              # Regex patterns for all timecode formats
├── error.py                # Custom exception classes
├── logging_config.py       # Logging setup with branch-aware default levels
└── __init__.py             # Package exports and convenience aliases
```

### Main Components

#### DfttTimecode Class (`dftt_timecode/core/dftt_timecode.py`)
- Core timecode class with all timecode operations
- Handles format conversion, arithmetic, and comparison operations
- Uses `fractions.Fraction` for high-precision internal timestamp storage

#### DfttTimeRange Class (`dftt_timecode/core/dftt_timerange.py`)
- Handles time intervals with start and end timecodes
- Supports range operations: intersection, union, containment checks
- Calculates duration and frame counts for ranges

#### Pattern Module (`dftt_timecode/pattern.py`)
- Contains regex patterns for all supported timecode formats
- Validates input strings before parsing
- Formats: SMPTE, SRT, FFMPEG, FCPX, DLP, frame count, timestamps

#### Error Module (`dftt_timecode/error.py`)
- Custom exception classes for timecode-specific errors, all inheriting from `DFTTError`
- Timecode errors: `DFTTTimecodeValueError`, `DFTTTimecodeInitializationError`, `DFTTTimecodeTypeError`, `DFTTTimecodeOperatorError`
- TimeRange errors: `DFTTTimeRangeMethodError`, `DFTTTimeRangeValueError`, `DFTTTimeRangeTypeError`, `DFTTTimeRangeFPSError`

#### Logging Module (`dftt_timecode/logging_config.py`)
- Provides `get_logger(name)` and `configure_logging(level)` (both re-exported at package level)
- Default level is branch-aware: `INFO` for installed packages and `main` branch, `DEBUG` for dev/feature branches
- Override via `DFTT_LOG_LEVEL` environment variable (`DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL`)

### Key Features
- **Multiple formats:** SMPTE (DF/NDF), SRT, FFMPEG, FCPX, DLP, frame count, timestamps
- **High frame rate:** 0.01-999.99 fps support
- **Strict mode:** 24-hour cycling for broadcast workflows
- **Rich operators:** Full arithmetic (+, -, *, /) and comparison (==, !=, <, >, <=, >=)
- **High precision:** Internal Fraction-based calculations for lossless accuracy
- **Convenience aliases:** `dtc` / `Timecode` (DfttTimecode), `dtr` / `Timerange` (DfttTimeRange)

### Timecode Types Supported
- `smpte`: Standard SMPTE format (01:23:45:12 or 01:23:45;12 for drop-frame)
- `srt`: SubRip format (01:23:45,678)
- `ffmpeg`: FFmpeg format (01:23:45.67)
- `fcpx`: Final Cut Pro X format (1/24s)
- `dlp`: DLP Cinema format (01:23:45:102)
- `frame`: Frame count (1000f)
- `time`: Timestamp in seconds (3600.0s)
- `auto`: Automatic detection based on input format

### Architecture Patterns
- **Single-dispatch methods:** Uses `functools.singledispatchmethod` for handling different input types
- **Input validation:** Comprehensive regex-based validation via pattern.py
- **Internal storage:** High-precision Fraction timestamps (no floating-point errors)
- **Lazy evaluation:** Format conversions computed on-demand
- **Immutability:** Operations return new instances rather than modifying in place

### Testing
- Uses pytest framework with parametrized tests
- Test files: `test/test_dftt_timecode.py`, `test/test_dftt_timerange.py`, `test/test_logging_config.py`
- Covers multiple timecode formats, edge cases, and error conditions
- Fixture-based test data setup

### Documentation System
- Sphinx with MyST-Parser (supports both RST and Markdown)
- Auto-generated API docs from docstrings
- Deployed to GitHub Pages via `.github/workflows/docs.yml`
- Changelog: Maintained in `CHANGELOG.md` (Keep a Changelog format), included in docs via RST
- Internationalization: Chinese translations under `docs/locale/`, built with `sphinx-intl`

### CI/CD Workflows
- **Documentation:** Builds and deploys to GitHub Pages on push to main (`.github/workflows/docs.yml`)
- **Publishing:** Automatically publishes to PyPI on GitHub release creation (`.github/workflows/publish-to-pypi.yml`)

## Version Information
- Current version: 1.0.0
- Python requirement: >=3.11
- Main dependencies: All standard library (fractions, logging, math, functools, re, subprocess)
- Dev dependencies: pytest, sphinx, pydata-sphinx-theme, myst-parser, sphinx-intl

## Common Usage Patterns

### Basic Timecode Creation
```python
from dftt_timecode import DfttTimecode, dtc

# Full class name
tc = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)

# Using convenience alias
tc = dtc('01:00:00:00', fps=24)

# Access properties
tc.type         # timecode format type
tc.fps          # frame rate
tc.framecount   # total frames from zero
tc.timestamp    # seconds from zero (float)
tc.precise_timestamp  # high-precision Fraction timestamp
```

### Format Conversion
```python
# Convert output format
tc.timecode_output('srt')   # SubRip format
tc.timecode_output('ffmpeg') # FFmpeg format

# Change timecode type
tc.set_type('smpte')
tc.set_fps(30, rounding=True)
tc.set_strict(False)
```

### Arithmetic Operations
```python
result = tc1 + tc2        # add timecodes
result = tc - 100         # subtract 100 frames
result = tc * 2           # multiply by factor
result = tc / 2           # divide by factor
result = tc + 1.0         # add 1 second (float)

# Comparisons
tc1 > tc2                 # compare timecodes
tc1 == tc2                # equality check
```

### TimeRange Operations
```python
from dftt_timecode import DfttTimeRange, dtr

# Create time range
tr = DfttTimeRange(start_tc='01:00:00:00', end_tc='02:00:00:00', fps=24)
# or using alias
tr = dtr('01:00:00:00', '02:00:00:00', fps=24)

# Access properties
tr.duration      # duration as DfttTimecode
tr.framecount    # total frames in range

# Range operations
tr1.intersection(tr2)  # overlapping portion
tr1.union(tr2)         # combined range
tc in tr               # check if timecode is in range
```
