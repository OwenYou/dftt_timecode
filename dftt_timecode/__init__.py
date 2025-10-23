"""
DFTT Timecode Library for Film and Television Production.

A high-precision timecode library supporting multiple professional formats including
SMPTE (drop-frame and non-drop-frame), SRT, FFmpeg, FCPX, DLP Cinema, and more.
Supports high frame rates from 0.01 to 999.99 fps with frame-accurate calculations.

Main Classes:
    - :class:`DfttTimecode`: Core timecode class with format conversion and arithmetic operations
    - :class:`DfttTimeRange`: Timerange class for working with time intervals

Convenience Aliases:
    - :func:`timecode`: Alias for DfttTimecode
    - :func:`dtc`: Short alias for DfttTimecode
    - :func:`timerange`: Alias for DfttTimeRange
    - :func:`dtr`: Short alias for DfttTimeRange

Example:
    >>> from dftt_timecode import DfttTimecode
    >>> tc = DfttTimecode('01:00:00:00', fps=24)
    >>> print(tc.timecode_output('srt'))
    01:00:00,000
    >>> tc2 = tc + 100  # Add 100 frames
    >>> print(tc2)
    01:00:04:04
"""

from dftt_timecode.core.dftt_timecode import DfttTimecode
from dftt_timecode.core.dftt_timerange import DfttTimeRange
from dftt_timecode.logging_config import configure_logging, get_logger

# Read version from package metadata (populated from pyproject.toml)
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("dftt-timecode")
    except PackageNotFoundError:
        # Package is not installed, use a fallback version
        __version__ = "0.0.0+dev"
except ImportError:
    # Python < 3.8 fallback (though we require 3.11+)
    __version__ = "0.0.0+dev"


# Aliases for easier importing
def timecode(*args, **kwargs) -> DfttTimecode:
    """Create a DfttTimecode instance.

    This is an alias for :class:`DfttTimecode` constructor.

    Args:
        *args: Positional arguments passed to DfttTimecode
        **kwargs: Keyword arguments passed to DfttTimecode

    Returns:
        DfttTimecode: A new timecode instance

    Example:
        >>> tc = timecode('01:00:00:00', fps=24)
    """
    return DfttTimecode(*args, **kwargs)


def timerange(*args, **kwargs) -> DfttTimeRange:
    """Create a DfttTimeRange instance.

    This is an alias for :class:`DfttTimeRange` constructor.

    Args:
        *args: Positional arguments passed to DfttTimeRange
        **kwargs: Keyword arguments passed to DfttTimeRange

    Returns:
        DfttTimeRange: A new timerange instance

    Example:
        >>> tr = timerange('01:00:00:00', '02:00:00:00', fps=24)
    """
    return DfttTimeRange(*args, **kwargs)


def dtc(*args, **kwargs) -> DfttTimecode:
    """Create a DfttTimecode instance (short alias).

    This is a short alias for :class:`DfttTimecode` constructor.

    Args:
        *args: Positional arguments passed to DfttTimecode
        **kwargs: Keyword arguments passed to DfttTimecode

    Returns:
        DfttTimecode: A new timecode instance

    Example:
        >>> tc = dtc('01:00:00:00', fps=24)
    """
    return DfttTimecode(*args, **kwargs)


def dtr(*args, **kwargs) -> DfttTimeRange:
    """Create a DfttTimeRange instance (short alias).

    This is a short alias for :class:`DfttTimeRange` constructor.

    Args:
        *args: Positional arguments passed to DfttTimeRange
        **kwargs: Keyword arguments passed to DfttTimeRange

    Returns:
        DfttTimeRange: A new timerange instance

    Example:
        >>> tr = dtr('01:00:00:00', '02:00:00:00', fps=24)
    """
    return DfttTimeRange(*args, **kwargs)

name = "dftt_timecode"
__author__ = "You Ziyuan"

__all__ = [
    "DfttTimecode",
    "DfttTimeRange",
    "timecode",
    "timerange",
    "dtc",
    "dtr",
    "configure_logging",
    "get_logger",
]
