from dftt_timecode.core.dftt_timecode import DfttTimecode
from dftt_timecode.core.dftt_timerange import DfttTimeRange


# Aliases for easier importing
def timecode(*args, **kwargs) -> DfttTimecode:
    """Alias for DfttTimecode."""
    return DfttTimecode(*args, **kwargs)


def timerange(*args, **kwargs) -> DfttTimeRange:
    """Alias for DfttTimeRange."""
    return DfttTimeRange(*args, **kwargs)


def dtc(*args, **kwargs) -> DfttTimecode:
    """Alias for DfttTimecode."""
    return DfttTimecode(*args, **kwargs)


def dtr(*args, **kwargs) -> DfttTimeRange:
    """Alias for DfttTimeRange."""
    return DfttTimeRange(*args, **kwargs)


name = "dftt_timecode"
__author__ = "You Ziyuan"
__version__ = "0.0.15a2"

__all__ = ["DfttTimecode", "DfttTimeRange", "timecode", "timerange", "dtc", "dtr"]
