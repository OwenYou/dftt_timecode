"""
Regular expression patterns for timecode format validation.

This module defines regex patterns for matching various professional timecode formats
used in film, television, and video production. All patterns support negative timecodes
with an optional leading minus sign.
"""

import re

SMPTE_NDF_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d):){1}(\d?\d\d{1}){1}$')
"""Regex pattern for SMPTE Non-Drop-Frame (NDF) timecode format.

Matches: ``HH:MM:SS:FF`` where frames use colon separator.

Examples:
    - Standard: ``01:23:45:12`` or ``-01:23:45:12``
    - High frame rate (>=100fps): ``01:01:23:45:102`` or ``-01:01:23:45:102``

Note:
    The colon separator before frames distinguishes NDF from drop-frame format.
"""

SMPTE_DF_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d);){1}(\d?\d\d{1}){1}$')
"""Regex pattern for SMPTE Drop-Frame (DF) timecode format.

Matches: ``HH:MM:SS;FF`` where frames use semicolon separator.

Examples:
    - Standard: ``01:23:45;12`` or ``-01:23:45;12``
    - High frame rate (>=100fps): ``01:00:00;102`` or ``-01:00:00;102``

Note:
    The semicolon separator before frames indicates drop-frame format.
    Used primarily with 29.97 fps and its multiples (59.94, 119.88).
"""

SMPTE_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d);?:?){1}(\d?\d\d{1}){1}$')
"""Regex pattern for any SMPTE timecode format (both NDF and DF).

Matches: ``HH:MM:SS:FF`` or ``HH:MM:SS;FF``

This is the union of :data:`SMPTE_NDF_REGEX` and :data:`SMPTE_DF_REGEX` patterns,
accepting either colon or semicolon before the frame number.
"""

SRT_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d),){1}(\d\d\d){1}$')
"""Regex pattern for SubRip (SRT) subtitle timecode format.

Matches: ``HH:MM:SS,mmm`` where mmm is milliseconds.

Examples:
    - Standard: ``01:23:45,678`` or ``-01:23:45,678``

Note:
    Uses comma separator before milliseconds. This format is frame rate independent.
"""

FFMPEG_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d)\.){1}(\d?\d+){1}$')
"""Regex pattern for FFmpeg timecode format.

Matches: ``HH:MM:SS.ss`` where ss is sub-seconds (centiseconds).

Examples:
    - Standard: ``01:23:45.67`` or ``-01:23:45.67``

Note:
    Uses period separator before sub-seconds. Commonly used in video processing tools.
"""

DLP_REGEX = re.compile(r'^(?:-)?(?:(?:(?:(\d\d{1}):){1}([0-5]?\d):){1}([0-5]?\d):){1}([01][0-9][0-9]|2[0-4][0-9]|25[0]){1}$')
"""Regex pattern for DLP Cinema timecode format.

Matches: ``HH:MM:SS:sss`` where sss is sub-frames (0-249).

Examples:
    - Standard: ``01:23:45:102`` or ``-01:23:45:102``

Note:
    DLP uses 250 sub-frames per second (4ms per sub-frame).
    See `CineCanvas specification <https://interop-docs.cinepedia.com/Reference_Documents/CineCanvas(tm)_RevC.pdf>`_ page 17.
"""

FCPX_REGEX = re.compile(r'^(?:-)?(\d+)[/](\d+)?s$')
"""Regex pattern for Final Cut Pro X (FCPX) rational time format.

Matches: ``numerator/denominator`` or ``numerator`` followed by ``s``.

Examples:
    - Fraction: ``1/24s`` or ``-1/24s``
    - Integer: ``1234s`` or ``-1234s``

Note:
    Represents time as a rational number (fraction) for precise calculations.
    The denominator is optional for integer values.
"""

FRAME_REGEX = re.compile(r'^(-?\d+?)f?$')
"""Regex pattern for frame count format.

Matches: Frame number with optional ``f`` suffix.

Examples:
    - With suffix: ``1234f`` or ``-1234f``
    - Without suffix: ``1234`` or ``-1234``

Note:
    Represents timecode as an absolute frame count. Requires frame rate for conversion.
"""

TIME_REGEX = re.compile(r'^(-?\d+?(\.{1})\d+?|-?\d+?)s?$')
"""Regex pattern for timestamp format in seconds.

Matches: Decimal or integer seconds with optional ``s`` suffix.

Examples:
    - Decimal: ``1234.5s`` or ``-1234.5``
    - Integer: ``1234s`` or ``-1234``

Note:
    Represents timecode as absolute seconds from zero. Most precise internal format.
"""


