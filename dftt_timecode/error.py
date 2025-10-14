"""
Custom exceptions for DFTT Timecode library.

This module defines all custom exception classes used throughout the DFTT Timecode library
for handling timecode-specific errors and timerange-specific errors.
"""


class DFTTError(Exception):
    """Base exception class for all DFTT Timecode library errors.

    All custom exceptions in this library inherit from this base class.
    """
    pass


class DFTTTimecodeValueError(DFTTError):
    """Raised when a timecode value is invalid or out of acceptable range.

    Examples include:
        - Frame number exceeding the frame rate limit
        - Invalid drop-frame timecode values
        - Illegal timecode values for the given parameters
    """
    pass


class DFTTTimecodeInitializationError(DFTTError):
    """Raised when timecode initialization fails due to incompatible parameters.

    Examples include:
        - Drop-frame status mismatch with timecode format
        - Incompatible timecode value and type combinations
    """
    pass


class DFTTTimecodeTypeError(DFTTError):
    """Raised when a timecode type is invalid or incompatible.

    Examples include:
        - Unknown timecode format type
        - Type mismatch between expected and actual timecode format
        - Invalid data type for timecode operations
    """
    pass


class DFTTTimecodeOperatorError(DFTTError):
    """Raised when an arithmetic or comparison operation on timecode objects fails.

    Examples include:
        - Operations between timecodes with different frame rates
        - Undefined operations (e.g., dividing number by timecode)
        - Invalid operand types for timecode arithmetic
    """
    pass


class DFTTTimeRangeMethodError(DFTTError):
    """Raised when a timerange method is called with invalid parameters or conditions.

    Examples include:
        - Attempting to intersect/union timeranges with different directions
        - Invalid offset or extend values
        - Operations on non-overlapping, non-adjacent timeranges
    """
    pass


class DFTTTimeRangeValueError(DFTTError):
    """Raised when a timerange value is invalid or out of acceptable range.

    Examples include:
        - Zero-length timerange
        - Duration exceeding 24 hours in strict mode
        - Invalid timerange separation parameters
    """
    pass


class DFTTTimeRangeTypeError(DFTTError):
    """Raised when a timerange type or operand type is invalid.

    Examples include:
        - Invalid item type for contains check
        - Attempting to operate on non-timerange objects
        - Type mismatches in timerange operations
    """
    pass


class DFTTTimeRangeFPSError(DFTTError):
    """Raised when timerange operations fail due to frame rate mismatches.

    Examples include:
        - FPS mismatch between start and end timecodes
        - Operations between timeranges with different frame rates
    """
    pass

