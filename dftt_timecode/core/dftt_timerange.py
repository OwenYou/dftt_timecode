"""
Timerange class for representing time intervals in DFTT Timecode library.

This module provides the DfttTimeRange class for working with time intervals,
supporting operations like offset, extend, intersection, union, and iteration.
"""

from fractions import Fraction
from typing import Optional, List, Iterator, Union

from dftt_timecode.core.dftt_timecode import DfttTimecode
from dftt_timecode.error import (
    DFTTError,
    DFTTTimeRangeFPSError,
    DFTTTimeRangeMethodError,
    DFTTTimeRangeTypeError,
    DFTTTimeRangeValueError,
)
from dftt_timecode.logging_config import get_logger

# Set up logger with automatic level detection based on git branch
logger = get_logger(__name__)


class DfttTimeRange:
    """High-precision timerange class for representing time intervals.

    DfttTimeRange represents a time interval with a start point, duration, and direction.
    It provides comprehensive operations for manipulating time ranges including offset,
    extend, shorten, reverse, retime, intersection, and union operations.

    The class uses :class:`fractions.Fraction` internally for precise calculations,
    ensuring frame-accurate operations even with complex interval manipulations.

    Args:
        start_tc: Start timecode. Can be a DfttTimecode object or any value
            that can construct a DfttTimecode. Required if not using precise parameters.
        end_tc: End timecode. Can be a DfttTimecode object or any value
            that can construct a DfttTimecode. Required if not using precise parameters.
        forward: Direction of the timerange. True for forward (start < end),
            False for backward (start > end). Defaults to True.
        fps: Frame rate in frames per second. Used when constructing timecodes
            from non-timecode values. Defaults to 24.0.
        start_precise_time: Internal construction parameter - precise start time
            as Fraction. Use with precise_duration for direct construction.
        precise_duration: Internal construction parameter - precise duration
            as Fraction. Use with start_precise_time for direct construction.
        strict_24h: Enable 24-hour constraint mode. When True, the timerange
            duration cannot exceed 24 hours and midnight-crossing ranges are
            handled specially. Defaults to False.

    Attributes:
        fps (float): Frame rate of the timerange
        forward (bool): Direction of the timerange
        strict_24h (bool): Whether 24-hour constraint is enabled
        precise_duration (Fraction): Duration as high-precision Fraction
        start_precise_time (Fraction): Start time as high-precision Fraction
        end_precise_time (Fraction): End time as high-precision Fraction
        duration (float): Duration in seconds (absolute value)
        framecount (int): Duration in frames (absolute value)
        start (DfttTimecode): Start timecode object
        end (DfttTimecode): End timecode object

    Raises:
        DFTTTimeRangeValueError: When creating zero-length or invalid timeranges
        DFTTTimeRangeFPSError: When start and end timecodes have mismatched fps
        ValueError: When neither (start_tc, end_tc) nor (start_precise_time, precise_duration) are provided

    Examples:
        Create from two timecodes::

            >>> tr = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24)
            >>> print(tr.duration)
            3600.0
            >>> print(tr.framecount)
            86400

        Create backward timerange::

            >>> tr = DfttTimeRange('02:00:00:00', '01:00:00:00', forward=False, fps=24)
            >>> print(tr.start)
            02:00:00:00
            >>> print(tr.end)
            01:00:00:00

        Operations::

            >>> tr = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)
            >>> tr2 = tr.offset(600)  # Move forward 600 seconds (10 minutes)
            >>> print(tr2.start)
            01:10:00:00
            >>> tr3 = tr.extend(300)  # Add 5 minutes to duration
            >>> print(tr3.duration)
            900.0

        Iteration::

            >>> tr = DfttTimeRange('01:00:00:00', '01:00:00:10', fps=24)
            >>> for tc in tr:
            ...     print(tc)
            01:00:00:00
            01:00:00:01
            ...
            01:00:00:09

        Set operations::

            >>> tr1 = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24)
            >>> tr2 = DfttTimeRange('01:30:00:00', '02:30:00:00', fps=24)
            >>> intersection = tr1 & tr2  # Intersection operator
            >>> print(intersection.start)
            01:30:00:00
            >>> union = tr1 | tr2  # Union operator
            >>> print(union.duration)
            5400.0

    Note:
        - Timerange objects are immutable. All operations return new instances.
        - The internal representation uses :class:`fractions.Fraction` for precision.
        - Forward and backward timeranges behave differently in some operations.
        - Zero-length timeranges are not allowed.

    See Also:
        - :class:`DfttTimecode`: For working with individual timecodes
        - :mod:`dftt_timecode.error`: Custom exception classes
    """

    TIME_24H_SECONDS = 86400
    """Constant representing 24 hours in seconds (86400)."""

    def __init__(
        self,
        start_tc=None,
        end_tc=None,
        forward: bool = True,
        fps=24.0,
        start_precise_time: Optional[Fraction] = None,
        precise_duration: Optional[Fraction] = None,
        strict_24h: bool = False,
    ):
        self.__fps = fps
        self.__forward = forward
        self.__strict_24h = strict_24h

        # Initialize based on construction method
        if start_precise_time is not None and precise_duration is not None:
            # Direct construction with precise values
            self.__start_precise_time = Fraction(start_precise_time)
            self.__precise_duration = Fraction(precise_duration)
            if self.__precise_duration == 0:
                raise DFTTTimeRangeValueError("Time range cannot be zero-length!")
        elif start_tc is not None and end_tc is not None:
            # Construction from start and end timecodes
            self._init_from_timecodes(start_tc, end_tc)
        else:
            raise DFTTTimeRangeValueError(
                "Must provide either start_tc+end_tc or start_precise_time+precise_duration"
            )

        # Validate 24h constraint
        if self.__strict_24h and abs(self.__precise_duration) > self.TIME_24H_SECONDS:
            logger.error(
                f"Duration {abs(self.__precise_duration)}s exceeds 24 hours ({self.TIME_24H_SECONDS}s) in strict mode"
            )
            raise DFTTTimeRangeValueError("Duration exceeds 24 hours in strict mode")

        logger.debug(
            f"TimeRange created: start={float(self.__start_precise_time):.3f}s, "
            f"duration={float(self.__precise_duration):.3f}s, fps={self.__fps}, "
            f"forward={self.__forward}, strict_24h={self.__strict_24h}"
        )

    def _init_from_timecodes(self, start_tc, end_tc):
        """Initialize from start and end timecodes"""
        # Convert inputs to DfttTimecode objects
        if isinstance(start_tc, DfttTimecode) and isinstance(end_tc, DfttTimecode):
            if start_tc.fps != end_tc.fps:
                logger.error(
                    f"FPS mismatch: start_tc fps={start_tc.fps}, end_tc fps={end_tc.fps}"
                )
                raise DFTTTimeRangeFPSError(
                    "FPS mismatch between start and end timecodes"
                )
            self.__fps = start_tc.fps
            start_precise = start_tc.precise_timestamp
            end_precise = end_tc.precise_timestamp
        elif isinstance(start_tc, DfttTimecode):
            self.__fps = start_tc.fps
            start_precise = start_tc.precise_timestamp
            end_tc = DfttTimecode(
                end_tc,
                fps=self.__fps,
                drop_frame=start_tc.is_drop_frame,
                strict=start_tc.is_strict,
            )
            end_precise = end_tc.precise_timestamp
        elif isinstance(end_tc, DfttTimecode):
            self.__fps = end_tc.fps
            end_precise = end_tc.precise_timestamp
            start_tc = DfttTimecode(
                start_tc,
                fps=self.__fps,
                drop_frame=end_tc.is_drop_frame,
                strict=end_tc.is_strict,
            )
            start_precise = start_tc.precise_timestamp
        else:
            start_tc = DfttTimecode(start_tc, fps=self.__fps)
            end_tc = DfttTimecode(end_tc, fps=self.__fps)
            start_precise = start_tc.precise_timestamp
            end_precise = end_tc.precise_timestamp

        # Calculate precise duration based on direction
        if self.__forward:
            self.__precise_duration = end_precise - start_precise
        else:
            self.__precise_duration = start_precise - end_precise

        # Handle midnight crossing in strict mode
        if self.__strict_24h and self.__precise_duration < 0:
            self.__precise_duration += self.TIME_24H_SECONDS

        if self.__precise_duration == 0:
            logger.error("Cannot create zero-length timerange")
            raise DFTTTimeRangeValueError("Time range cannot be zero-length!")

        self.__start_precise_time = start_precise

    @property
    def fps(self) -> float:
        """Frame rate of the timerange"""
        return self.__fps

    @property
    def forward(self) -> bool:
        """Direction of the timerange"""
        return self.__forward

    @property
    def strict_24h(self) -> bool:
        """Whether timerange is constrained to 24 hours"""
        return self.__strict_24h

    @property
    def precise_duration(self) -> Fraction:
        """Precise duration as Fraction to avoid calculation errors"""
        return self.__precise_duration

    @property
    def start_precise_time(self) -> Fraction:
        """Start time as precise Fraction"""
        return self.__start_precise_time

    @property
    def end_precise_time(self) -> Fraction:
        """End time as precise Fraction"""
        if self.__forward:
            return self.__start_precise_time + self.__precise_duration
        else:
            return self.__start_precise_time - self.__precise_duration

    @property
    def duration(self) -> float:
        """Duration in seconds"""
        return float(abs(self.__precise_duration))

    @property
    def framecount(self) -> int:
        """Duration in frames"""
        return int(round(float(abs(self.__precise_duration)) * self.__fps))

    @property
    def start(self) -> DfttTimecode:
        """Start timecode"""
        return DfttTimecode(float(self.__start_precise_time), fps=self.__fps)

    @property
    def end(self) -> DfttTimecode:
        """End timecode"""
        return DfttTimecode(float(self.end_precise_time), fps=self.__fps)

    # Core timerange operations
    def offset(self, offset_value: Union[float, DfttTimecode, str, int]) -> "DfttTimeRange":
        """Move timerange in time while preserving duration.

        Shifts the entire timerange by the specified offset amount without
        changing the duration. Both start and end points move by the same amount.

        Args:
            offset_value: Amount to offset the timerange. Can be:
                - float: Seconds to shift
                - int: Frames to shift (converted using current fps)
                - DfttTimecode: Uses the timecode's timestamp
                - str: Timecode string to parse

        Returns:
            DfttTimeRange: New timerange with shifted start/end points

        Raises:
            DFTTTimeRangeMethodError: If offset_value cannot be parsed

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)
            >>> tr2 = tr.offset(600)  # Offset by 10 minutes (600 seconds)
            >>> print(tr2.start)
            01:10:00:00
            >>> print(tr2.end)
            01:20:00:00

        Note:
            In strict_24h mode, the new start time wraps around at 24 hours.
        """
        try:
            if isinstance(offset_value, float):
                offset_precise = Fraction(offset_value)
            elif isinstance(offset_value, DfttTimecode):
                offset_precise = offset_value.precise_timestamp
            else:
                offset_tc = DfttTimecode(offset_value, fps=self.__fps)
                offset_precise = offset_tc.precise_timestamp

            new_start = self.__start_precise_time + offset_precise

            # Handle 24h constraint
            if self.__strict_24h:
                new_start = new_start % self.TIME_24H_SECONDS

            logger.debug(
                f"Offset timerange by {float(offset_precise):.3f}s: "
                f"old_start={float(self.__start_precise_time):.3f}s, "
                f"new_start={float(new_start):.3f}s"
            )

            return DfttTimeRange(
                start_precise_time=new_start,
                precise_duration=self.__precise_duration,
                forward=self.__forward,
                fps=self.__fps,
                strict_24h=self.__strict_24h,
            )
        except Exception:
            raise DFTTTimeRangeMethodError(f"Invalid offset value {offset_value}")

    def extend(self, extend_value: Union[int, float, DfttTimecode, str]) -> "DfttTimeRange":
        """Extend duration (positive value increases duration).

        Extends or shortens the timerange by modifying the end point while
        keeping the start point fixed. Positive values increase duration,
        negative values decrease it.

        Args:
            extend_value: Amount to extend the duration. Can be:
                - int or float: Seconds to extend (positive) or shorten (negative)
                - DfttTimecode: Uses the timecode's timestamp
                - str: Timecode string to parse

        Returns:
            DfttTimeRange: New timerange with modified duration

        Raises:
            DFTTTimeRangeValueError: If extension results in zero-length timerange
                or exceeds 24 hours in strict mode
            DFTTTimeRangeMethodError: If extend_value cannot be parsed

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)
            >>> tr2 = tr.extend(300)  # Add 5 minutes
            >>> print(tr2.duration)
            900.0
            >>> tr3 = tr.extend(-300)  # Subtract 5 minutes
            >>> print(tr3.duration)
            300.0

        Note:
            The direction (forward/backward) affects how extension is applied.
        """
        try:
            if isinstance(extend_value, (int, float)):
                extend_precise = Fraction(extend_value)
            elif isinstance(extend_value, DfttTimecode):
                extend_precise = extend_value.precise_timestamp
            else:
                extend_tc = DfttTimecode(extend_value, fps=self.__fps)
                extend_precise = extend_tc.precise_timestamp

            new_duration = self.__precise_duration + (
                extend_precise if self.__forward else -extend_precise
            )

            if new_duration == 0:
                logger.error("Cannot create zero-length timerange via extend")
                raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

            # Handle 24h constraint
            if self.__strict_24h and abs(new_duration) > self.TIME_24H_SECONDS:
                logger.error(
                    f"Extended duration {abs(new_duration):.3f}s exceeds 24 hours in strict mode"
                )
                raise DFTTTimeRangeValueError(
                    "Duration exceeds 24 hours in strict mode"
                )

            logger.debug(
                f"Extend timerange by {float(extend_precise):.3f}s: "
                f"old_duration={float(self.__precise_duration):.3f}s, "
                f"new_duration={float(new_duration):.3f}s"
            )

            return DfttTimeRange(
                start_precise_time=self.__start_precise_time,
                precise_duration=new_duration,
                forward=self.__forward,
                fps=self.__fps,
                strict_24h=self.__strict_24h,
            )
        except Exception as e:
            if isinstance(e, DFTTTimeRangeValueError):
                raise
            raise DFTTTimeRangeMethodError("Invalid extend value")

    def shorten(self, shorten_value: Union[int, float, DfttTimecode, str]) -> "DfttTimeRange":
        """Shorten duration (positive value decreases duration).

        This is a convenience method that calls :meth:`extend` with a negated value.
        Shortens the timerange by modifying the end point while keeping the start fixed.

        Args:
            shorten_value: Amount to shorten the duration. Can be:
                - int or float: Seconds to shorten (positive decreases duration)
                - DfttTimecode: Uses the timecode's timestamp
                - str: Timecode string to parse

        Returns:
            DfttTimeRange: New timerange with shortened duration

        Raises:
            DFTTTimeRangeValueError: If shortening results in zero-length timerange
            DFTTTimeRangeMethodError: If shorten_value cannot be parsed

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)
            >>> tr2 = tr.shorten(300)  # Shorten by 5 minutes
            >>> print(tr2.duration)
            300.0
            >>> print(tr2.end)
            01:05:00:00

        Note:
            Internally calls ``extend(-shorten_value)`` for numeric values.
        """
        return self.extend(
            -shorten_value if isinstance(shorten_value, (int, float)) else shorten_value
        )

    def reverse(self) -> "DfttTimeRange":
        """Reverse direction of timerange.

        Creates a new timerange with swapped start/end points and inverted direction.
        The duration magnitude remains the same, but the direction is flipped.

        Returns:
            DfttTimeRange: New timerange with reversed direction

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24, forward=True)
            >>> print(tr.start, '->', tr.end)
            01:00:00:00 -> 02:00:00:00
            >>> tr_rev = tr.reverse()
            >>> print(tr_rev.start, '->', tr_rev.end)
            02:00:00:00 -> 01:00:00:00
            >>> print(tr_rev.forward)
            False
            >>> print(tr.duration == tr_rev.duration)
            True

        Note:
            - The new start becomes the old end
            - The forward flag is flipped
            - Duration magnitude is preserved
            - This is useful for working with timeranges that play backward
        """
        logger.debug(
            f"Reversing timerange: forward={self.__forward} -> {not self.__forward}"
        )
        return DfttTimeRange(
            start_precise_time=self.end_precise_time,
            precise_duration=self.__precise_duration,
            forward=not self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def retime(self, retime_factor: Union[int, float, Fraction]) -> "DfttTimeRange":
        """Change duration by multiplication factor.

        Scales the timerange duration by the given factor while keeping the start
        point fixed. This is useful for time-stretching or speed-change operations.

        Args:
            retime_factor: Multiplication factor for the duration. Can be:
                - int or float: Factor to multiply duration by
                - Fraction: Precise rational factor
                Examples: 2.0 doubles duration, 0.5 halves it, 1.5 extends by 50%

        Returns:
            DfttTimeRange: New timerange with scaled duration

        Raises:
            DFTTTimeRangeTypeError: If retime_factor is not numeric
            DFTTTimeRangeValueError: If retime_factor is 0, or if result exceeds
                24 hours in strict_24h mode

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)
            >>> print(tr.duration)
            600.0
            >>> tr2 = tr.retime(2.0)  # Double the duration
            >>> print(tr2.duration)
            1200.0
            >>> print(tr2.end)
            01:20:00:00
            >>> tr3 = tr.retime(0.5)  # Half the duration (speed up)
            >>> print(tr3.duration)
            300.0
            >>> # Can also use * operator
            >>> tr4 = tr * 2
            >>> print(tr4.duration)
            1200.0

        Note:
            - Start point remains unchanged
            - Commonly used for speed ramping or time-stretching effects
            - Factor > 1 increases duration (slow down)
            - Factor < 1 decreases duration (speed up)
            - Can also use the ``*`` operator for the same effect
        """
        if not isinstance(retime_factor, (int, float, Fraction)):
            logger.error(f"Retime factor must be numeric, got {type(retime_factor)}")
            raise DFTTTimeRangeTypeError("Retime factor must be numeric")

        if retime_factor == 0:
            logger.error("Cannot retime to zero duration")
            raise DFTTTimeRangeValueError("Cannot retime to zero duration")

        new_duration = self.__precise_duration * Fraction(retime_factor)

        if self.__strict_24h and abs(new_duration) > self.TIME_24H_SECONDS:
            logger.error(
                f"Retimed duration {abs(new_duration):.3f}s exceeds 24 hours in strict mode"
            )
            raise DFTTTimeRangeValueError("Duration exceeds 24 hours in strict mode")

        logger.debug(
            f"Retime timerange by factor {retime_factor}: "
            f"old_duration={float(self.__precise_duration):.3f}s, "
            f"new_duration={float(new_duration):.3f}s"
        )

        return DfttTimeRange(
            start_precise_time=self.__start_precise_time,
            precise_duration=new_duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def separate(self, num_parts: int) -> List["DfttTimeRange"]:
        """Separate timerange into multiple equal parts.

        Divides the timerange into a specified number of equal-duration sub-ranges.
        All parts have the same duration and are contiguous (adjacent with no gaps).

        Args:
            num_parts: Number of parts to divide the timerange into (must be >= 2)

        Returns:
            List[DfttTimeRange]: List of timerange parts, ordered from start to end

        Raises:
            DFTTTimeRangeValueError: If num_parts is less than 2

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '01:01:00:00', fps=24)
            >>> parts = tr.separate(4)  # Split into 4 equal parts
            >>> len(parts)
            4
            >>> for i, part in enumerate(parts):
            ...     print(f"Part {i+1}: {part.start} - {part.end}, duration={part.duration}")
            Part 1: 01:00:00:00 - 01:00:15:00, duration=15.0
            Part 2: 01:00:15:00 - 01:00:30:00, duration=15.0
            Part 3: 01:00:30:00 - 01:00:45:00, duration=15.0
            Part 4: 01:00:45:00 - 01:01:00:00, duration=15.0
            >>> # Each part has equal duration
            >>> all(part.duration == tr.duration / 4 for part in parts)
            True

        Note:
            - Each part has duration = original_duration / num_parts
            - Parts are contiguous (no gaps or overlaps)
            - All parts inherit the same fps, forward direction, and strict_24h mode
            - For backward timeranges, parts are still ordered from start to end
            - Useful for splitting work into parallel chunks or creating segments
        """
        if num_parts < 2:
            logger.error(f"Cannot separate into {num_parts} parts, must be >= 2")
            raise DFTTTimeRangeValueError("Must separate into at least 2 parts")

        part_duration = self.__precise_duration / num_parts
        logger.debug(
            f"Separating timerange into {num_parts} parts, each with duration={float(part_duration):.3f}s"
        )
        parts = []

        for i in range(num_parts):
            part_start = self.__start_precise_time + (
                i * part_duration if self.__forward else -i * part_duration
            )
            parts.append(
                DfttTimeRange(
                    start_precise_time=part_start,
                    precise_duration=part_duration,
                    forward=self.__forward,
                    fps=self.__fps,
                    strict_24h=self.__strict_24h,
                )
            )

        return parts

    # Operations with other timeranges
    def contains(self, item: Union[DfttTimecode, 'DfttTimeRange', str, int, float], strict_forward: bool = False) -> bool:
        """Check if timerange contains another timerange or timecode.

        Args:
            item: Item to check for containment. Can be:
                - DfttTimecode: Checks if timecode is within range
                - DfttTimeRange: Checks if entire timerange is contained
                - str, int, float: Converted to timecode for checking
            strict_forward: If True, requires contained timerange to have same
                direction. Only applies when item is a DfttTimeRange. Defaults to False.

        Returns:
            bool: True if item is contained within this timerange, False otherwise

        Raises:
            DFTTTimeRangeTypeError: If item cannot be converted to timecode

        Examples:
            >>> tr = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24)
            >>> tc = DfttTimecode('01:30:00:00', fps=24)
            >>> tr.contains(tc)
            True
            >>> tr.contains('00:30:00:00')
            False
            >>> tr2 = DfttTimeRange('01:10:00:00', '01:50:00:00', fps=24)
            >>> tr.contains(tr2)
            True

        Note:
            For backward timeranges, containment is checked accordingly.
        """
        if isinstance(item, DfttTimecode):
            item_time = item.precise_timestamp
            start_time = self.__start_precise_time
            end_time = self.end_precise_time

            if self.__forward:
                return start_time <= item_time <= end_time
            else:
                return end_time <= item_time <= start_time

        elif isinstance(item, DfttTimeRange):
            if strict_forward and item.forward != self.__forward:
                return False

            item_start = item.start_precise_time
            item_end = item.end_precise_time

            return self.contains(
                DfttTimecode(float(item_start), fps=self.__fps)
            ) and self.contains(DfttTimecode(float(item_end), fps=self.__fps))
        else:
            try:
                tc = DfttTimecode(item, fps=self.__fps)
                return self.contains(tc)
            except DFTTError:
                raise DFTTTimeRangeTypeError("Invalid item type for contains check")

    def intersect(self, other: "DfttTimeRange") -> Optional["DfttTimeRange"]:
        """Calculate intersection of two timeranges (AND operation).

        Returns the overlapping portion of two timeranges. Both timeranges must
        have the same direction and frame rate.

        Args:
            other: Another DfttTimeRange to intersect with

        Returns:
            DfttTimeRange: New timerange representing the intersection, or None if no overlap

        Raises:
            DFTTTimeRangeTypeError: If other is not a DfttTimeRange
            DFTTTimeRangeMethodError: If timeranges have different directions
            DFTTTimeRangeFPSError: If timeranges have different frame rates

        Examples:
            >>> tr1 = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24)
            >>> tr2 = DfttTimeRange('01:30:00:00', '02:30:00:00', fps=24)
            >>> intersection = tr1.intersect(tr2)
            >>> print(intersection.start)
            01:30:00:00
            >>> print(intersection.end)
            02:00:00:00
            >>> # Can also use & operator
            >>> intersection = tr1 & tr2

        Note:
            - Returns None if timeranges don't overlap
            - Strict_24h is True only if both input timeranges have it enabled
        """
        if not isinstance(other, DfttTimeRange):
            logger.error(f"Can only intersect with DfttTimeRange, got {type(other)}")
            raise DFTTTimeRangeTypeError(
                "Can only intersect with another DfttTimeRange"
            )

        if self.__forward != other.forward:
            logger.error(
                f"Cannot intersect timeranges with different directions: "
                f"self.forward={self.__forward}, other.forward={other.forward}"
            )
            raise DFTTTimeRangeMethodError(
                "Cannot intersect timeranges with different directions"
            )

        if self.__fps != other.fps:
            logger.error(
                f"Cannot intersect timeranges with different FPS: "
                f"self.fps={self.__fps}, other.fps={other.fps}"
            )
            raise DFTTTimeRangeFPSError(
                "Cannot intersect timeranges with different FPS"
            )

        # Calculate intersection bounds
        if self.__forward:
            start = max(self.__start_precise_time, other.start_precise_time)
            end = min(self.end_precise_time, other.end_precise_time)
        else:
            start = min(self.__start_precise_time, other.start_precise_time)
            end = max(self.end_precise_time, other.end_precise_time)

        if (self.__forward and start >= end) or (not self.__forward and start <= end):
            logger.debug("No intersection found between timeranges")
            return None  # No intersection

        duration = end - start if self.__forward else start - end
        logger.debug(
            f"Intersection found: start={float(start):.3f}s, duration={float(duration):.3f}s"
        )

        return DfttTimeRange(
            start_precise_time=start,
            precise_duration=duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h and other.strict_24h,
        )

    def union(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Calculate union of two timeranges (OR operation).

        Combines two overlapping or adjacent timeranges into a single continuous
        timerange that spans from the earliest start to the latest end. Both
        timeranges must have the same direction and frame rate, and must either
        overlap or be adjacent (touching) with no gap between them.

        Args:
            other: Another DfttTimeRange to union with

        Returns:
            DfttTimeRange: New timerange spanning both input ranges

        Raises:
            DFTTTimeRangeTypeError: If other is not a DfttTimeRange
            DFTTTimeRangeMethodError: If timeranges have different directions,
                or if they are non-overlapping and non-adjacent (have a gap)
            DFTTTimeRangeFPSError: If timeranges have different frame rates

        Examples:
            Overlapping timeranges::

                >>> tr1 = DfttTimeRange('01:00:00:00', '01:30:00:00', fps=24)
                >>> tr2 = DfttTimeRange('01:20:00:00', '02:00:00:00', fps=24)
                >>> union = tr1.union(tr2)
                >>> print(union.start)
                01:00:00:00
                >>> print(union.end)
                02:00:00:00
                >>> print(union.duration)
                3600.0

            Adjacent (touching) timeranges::

                >>> tr1 = DfttTimeRange('01:00:00:00', '01:30:00:00', fps=24)
                >>> tr2 = DfttTimeRange('01:30:00:00', '02:00:00:00', fps=24)
                >>> union = tr1.union(tr2)  # No gap, they touch
                >>> print(union.start)
                01:00:00:00
                >>> print(union.end)
                02:00:00:00

            Using the | operator::

                >>> tr1 = DfttTimeRange('01:00:00:00', '01:30:00:00', fps=24)
                >>> tr2 = DfttTimeRange('01:20:00:00', '02:00:00:00', fps=24)
                >>> union = tr1 | tr2  # Shorthand for union
                >>> print(union.duration)
                3600.0

            Non-adjacent timeranges (will fail)::

                >>> tr1 = DfttTimeRange('01:00:00:00', '01:30:00:00', fps=24)
                >>> tr2 = DfttTimeRange('02:00:00:00', '02:30:00:00', fps=24)
                >>> union = tr1.union(tr2)  # Gap of 30 minutes
                DFTTTimeRangeMethodError: Cannot union non-overlapping, non-adjacent timeranges

        Note:
            - Timeranges must overlap or be adjacent (no gap allowed)
            - The result spans from earliest start to latest end
            - Direction must be the same for both timeranges
            - Strict_24h is True only if both input timeranges have it enabled
            - This is a set operation, different from :meth:`add` which combines durations
            - Can also use the ``|`` operator as a shorthand
            - For checking overlap, use :meth:`intersect` first

        See Also:
            - :meth:`intersect`: Get the overlapping portion (AND operation)
            - :meth:`add`: Add durations (different from union)
        """
        if not isinstance(other, DfttTimeRange):
            logger.error(f"Can only union with DfttTimeRange, got {type(other)}")
            raise DFTTTimeRangeTypeError("Can only union with another DfttTimeRange")

        if self.__forward != other.forward:
            logger.error(
                f"Cannot union timeranges with different directions: "
                f"self.forward={self.__forward}, other.forward={other.forward}"
            )
            raise DFTTTimeRangeMethodError(
                "Cannot union timeranges with different directions"
            )

        if self.__fps != other.fps:
            logger.error(
                f"Cannot union timeranges with different FPS: "
                f"self.fps={self.__fps}, other.fps={other.fps}"
            )
            raise DFTTTimeRangeFPSError("Cannot union timeranges with different FPS")

        # Check for overlap or adjacency
        if self.intersect(other) is None:
            # Check if they are adjacent
            if self.__forward:
                if not (
                    self.end_precise_time == other.start_precise_time
                    or other.end_precise_time == self.__start_precise_time
                ):
                    logger.error(
                        "Cannot union non-overlapping, non-adjacent timeranges: "
                        f"self=[{float(self.__start_precise_time):.3f}s, {float(self.end_precise_time):.3f}s], "
                        f"other=[{float(other.start_precise_time):.3f}s, {float(other.end_precise_time):.3f}s]"
                    )
                    raise DFTTTimeRangeMethodError(
                        "Cannot union non-overlapping, non-adjacent timeranges"
                    )
            else:
                if not (
                    self.end_precise_time == other.start_precise_time
                    or other.end_precise_time == self.__start_precise_time
                ):
                    logger.error(
                        "Cannot union non-overlapping, non-adjacent timeranges (backward)"
                    )
                    raise DFTTTimeRangeMethodError(
                        "Cannot union non-overlapping, non-adjacent timeranges"
                    )

        # Calculate union bounds
        if self.__forward:
            start = min(self.__start_precise_time, other.start_precise_time)
            end = max(self.end_precise_time, other.end_precise_time)
        else:
            start = max(self.__start_precise_time, other.start_precise_time)
            end = min(self.end_precise_time, other.end_precise_time)

        duration = end - start if self.__forward else start - end

        logger.debug(
            f"Union created: start={float(start):.3f}s, duration={float(duration):.3f}s"
        )

        return DfttTimeRange(
            start_precise_time=start,
            precise_duration=duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h and other.strict_24h,
        )

    def add(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Add durations of two timeranges (direction-sensitive).

        Combines the durations of two timeranges to create a new timerange with
        extended duration. The behavior depends on whether the timeranges have
        the same or opposite directions.

        Args:
            other: Another DfttTimeRange to add

        Returns:
            DfttTimeRange: New timerange with combined duration, same start point
                and direction as the original

        Raises:
            DFTTTimeRangeTypeError: If other is not a DfttTimeRange
            DFTTTimeRangeFPSError: If timeranges have different frame rates
            DFTTTimeRangeValueError: If result is zero-length

        Examples:
            >>> tr1 = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)  # 10 min
            >>> tr2 = DfttTimeRange('01:00:00:00', '01:05:00:00', fps=24)  # 5 min
            >>> tr3 = tr1.add(tr2)
            >>> print(tr3.duration)  # Same direction: 10 + 5 = 15 min
            900.0
            >>> tr4 = DfttTimeRange('01:10:00:00', '01:00:00:00', forward=False, fps=24)
            >>> tr5 = tr1.add(tr4)
            >>> print(tr5.duration)  # Opposite direction: 10 - 10 = 0 (error)
            DFTTTimeRangeValueError

        Note:
            - Same direction: durations are added (extend)
            - Opposite direction: durations are subtracted (shorten)
            - Start point remains unchanged
            - This is different from :meth:`union` which combines overlapping ranges
        """
        if not isinstance(other, DfttTimeRange):
            logger.error(f"Can only add DfttTimeRange, got {type(other)}")
            raise DFTTTimeRangeTypeError("Can only add another DfttTimeRange")

        if self.__fps != other.fps:
            logger.error(
                f"Cannot add timeranges with different FPS: "
                f"self.fps={self.__fps}, other.fps={other.fps}"
            )
            raise DFTTTimeRangeFPSError("Cannot add timeranges with different FPS")

        # Direction sensitive addition
        if self.__forward == other.forward:
            new_duration = self.__precise_duration + other.precise_duration
        else:
            new_duration = self.__precise_duration - other.precise_duration

        if new_duration == 0:
            logger.error("Add operation resulted in zero-length timerange")
            raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

        logger.debug(
            f"Add timerange: same_direction={self.__forward == other.forward}, "
            f"old_duration={float(self.__precise_duration):.3f}s, "
            f"new_duration={float(new_duration):.3f}s"
        )

        return DfttTimeRange(
            start_precise_time=self.__start_precise_time,
            precise_duration=new_duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def subtract(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Subtract durations of two timeranges (direction-sensitive).

        Subtracts the duration of another timerange from this one to create a new
        timerange with reduced duration. The behavior depends on whether the
        timeranges have the same or opposite directions.

        Args:
            other: Another DfttTimeRange to subtract

        Returns:
            DfttTimeRange: New timerange with reduced duration, same start point
                and direction as the original

        Raises:
            DFTTTimeRangeTypeError: If other is not a DfttTimeRange
            DFTTTimeRangeFPSError: If timeranges have different frame rates
            DFTTTimeRangeValueError: If result is zero-length

        Examples:
            >>> tr1 = DfttTimeRange('01:00:00:00', '01:10:00:00', fps=24)  # 10 min
            >>> tr2 = DfttTimeRange('01:00:00:00', '01:03:00:00', fps=24)  # 3 min
            >>> tr3 = tr1.subtract(tr2)
            >>> print(tr3.duration)  # Same direction: 10 - 3 = 7 min
            420.0
            >>> print(tr3.end)
            01:07:00:00
            >>> # With opposite directions
            >>> tr4 = DfttTimeRange('01:10:00:00', '01:08:00:00', forward=False, fps=24)
            >>> tr5 = tr1.subtract(tr4)  # 10 - (-2) = 12 min
            >>> print(tr5.duration)
            720.0

        Note:
            - Same direction: durations are subtracted (shorten)
            - Opposite direction: durations are added (extend)
            - Start point remains unchanged
            - This is the inverse operation of :meth:`add`
            - Can result in zero-length error if durations are equal
        """
        if not isinstance(other, DfttTimeRange):
            logger.error(f"Can only subtract DfttTimeRange, got {type(other)}")
            raise DFTTTimeRangeTypeError("Can only subtract another DfttTimeRange")

        if self.__fps != other.fps:
            logger.error(
                f"Cannot subtract timeranges with different FPS: "
                f"self.fps={self.__fps}, other.fps={other.fps}"
            )
            raise DFTTTimeRangeFPSError("Cannot subtract timeranges with different FPS")

        # Direction sensitive subtraction
        if self.__forward == other.forward:
            new_duration = self.__precise_duration - other.precise_duration
        else:
            new_duration = self.__precise_duration + other.precise_duration

        if new_duration == 0:
            logger.error("Subtract operation resulted in zero-length timerange")
            raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

        logger.debug(
            f"Subtract timerange: same_direction={self.__forward == other.forward}, "
            f"old_duration={float(self.__precise_duration):.3f}s, "
            f"new_duration={float(new_duration):.3f}s"
        )

        return DfttTimeRange(
            start_precise_time=self.__start_precise_time,
            precise_duration=new_duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    # Magic methods and utilities
    def __str__(self) -> str:
        return f"DfttTimeRange({self.start},{self.end},fps={self.__fps},forward={self.__forward})"

    def __repr__(self) -> str:
        return f"DfttTimeRange(start_precise_time={self.__start_precise_time}, precise_duration={self.__precise_duration}, forward={self.__forward}, fps={self.__fps}, strict_24h={self.__strict_24h})"

    def __len__(self) -> int:
        return self.framecount

    def __contains__(self, item) -> bool:
        return self.contains(item)

    def __iter__(self) -> Iterator[DfttTimecode]:
        """Iterate through timecodes in the range"""
        current_time = self.__start_precise_time
        frame_duration = Fraction(1) / self.__fps

        if self.__forward:
            while current_time < self.end_precise_time:
                yield DfttTimecode(float(current_time), fps=self.__fps)
                current_time += frame_duration
        else:
            while current_time > self.end_precise_time:
                yield DfttTimecode(float(current_time), fps=self.__fps)
                current_time -= frame_duration

    def __add__(self, other) -> "DfttTimeRange":
        """Add operator for timeranges"""
        if isinstance(other, DfttTimeRange):
            return self.add(other)
        else:
            # Treat as offset
            return self.offset(other)

    def __sub__(self, other) -> "DfttTimeRange":
        """Subtract operator for timeranges"""
        if isinstance(other, DfttTimeRange):
            return self.subtract(other)
        else:
            # Treat as negative offset
            return self.offset(-other if isinstance(other, (int, float)) else other)

    def __mul__(self, factor) -> "DfttTimeRange":
        """Multiply duration by factor"""
        return self.retime(factor)

    def __truediv__(self, factor) -> "DfttTimeRange":
        """Divide duration by factor"""
        return self.retime(1 / factor)

    def __and__(self, other) -> Optional["DfttTimeRange"]:
        """Intersection operator"""
        return self.intersect(other)

    def __or__(self, other) -> "DfttTimeRange":
        """Union operator"""
        return self.union(other)

    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, DfttTimeRange):
            return False
        return (
            self.__start_precise_time == other.start_precise_time
            and self.__precise_duration == other.precise_duration
            and self.__forward == other.forward
            and self.__fps == other.fps
        )

    def __ne__(self, other) -> bool:
        """Inequality comparison"""
        return not self.__eq__(other)

    def __lt__(self, other) -> bool:
        """Less than comparison based on start time"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError("Cannot compare with non-DfttTimeRange")
        return self.__start_precise_time < other.start_precise_time

    def __le__(self, other) -> bool:
        """Less than or equal comparison"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        """Greater than comparison"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError("Cannot compare with non-DfttTimeRange")
        return self.__start_precise_time > other.start_precise_time

    def __ge__(self, other) -> bool:
        """Greater than or equal comparison"""
        return self.__gt__(other) or self.__eq__(other)
