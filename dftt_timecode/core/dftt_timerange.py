from fractions import Fraction
from typing import Optional, List, Iterator

from dftt_timecode.core.dftt_timecode import DfttTimecode
from dftt_timecode.error import (
    DFTTError,
    DFTTTimeRangeFPSError,
    DFTTTimeRangeMethodError,
    DFTTTimeRangeTypeError,
    DFTTTimeRangeValueError,
)


class DfttTimeRange:
    TIME_24H_SECONDS = 86400

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
            raise DFTTTimeRangeValueError("Duration exceeds 24 hours in strict mode")

    def _init_from_timecodes(self, start_tc, end_tc):
        """Initialize from start and end timecodes"""
        # Convert inputs to DfttTimecode objects
        if isinstance(start_tc, DfttTimecode) and isinstance(end_tc, DfttTimecode):
            if start_tc.fps != end_tc.fps:
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
    def offset(self, offset_value) -> "DfttTimeRange":
        """Move timerange in time while preserving duration"""
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

            return DfttTimeRange(
                start_precise_time=new_start,
                precise_duration=self.__precise_duration,
                forward=self.__forward,
                fps=self.__fps,
                strict_24h=self.__strict_24h,
            )
        except Exception:
            raise DFTTTimeRangeMethodError(f"Invalid offset value {offset_value}")

    def extend(self, extend_value) -> "DfttTimeRange":
        """Extend duration (positive value increases duration)"""
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
                raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

            # Handle 24h constraint
            if self.__strict_24h and abs(new_duration) > self.TIME_24H_SECONDS:
                raise DFTTTimeRangeValueError(
                    "Duration exceeds 24 hours in strict mode"
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

    def shorten(self, shorten_value) -> "DfttTimeRange":
        """Shorten duration (positive value decreases duration)"""
        return self.extend(
            -shorten_value if isinstance(shorten_value, (int, float)) else shorten_value
        )

    def reverse(self) -> "DfttTimeRange":
        """Reverse direction of timerange"""
        return DfttTimeRange(
            start_precise_time=self.end_precise_time,
            precise_duration=self.__precise_duration,
            forward=not self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def retime(self, retime_factor) -> "DfttTimeRange":
        """Change duration by multiplication factor"""
        if not isinstance(retime_factor, (int, float, Fraction)):
            raise DFTTTimeRangeTypeError("Retime factor must be numeric")

        if retime_factor == 0:
            raise DFTTTimeRangeValueError("Cannot retime to zero duration")

        new_duration = self.__precise_duration * Fraction(retime_factor)

        if self.__strict_24h and abs(new_duration) > self.TIME_24H_SECONDS:
            raise DFTTTimeRangeValueError("Duration exceeds 24 hours in strict mode")

        return DfttTimeRange(
            start_precise_time=self.__start_precise_time,
            precise_duration=new_duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def separate(self, num_parts: int) -> List["DfttTimeRange"]:
        """Separate timerange into multiple equal parts"""
        if num_parts < 2:
            raise DFTTTimeRangeValueError("Must separate into at least 2 parts")

        part_duration = self.__precise_duration / num_parts
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
    def contains(self, item, strict_forward: bool = False) -> bool:
        """Check if timerange contains another timerange or timecode"""
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
        """Intersection operation (AND) - requires same direction"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError(
                "Can only intersect with another DfttTimeRange"
            )

        if self.__forward != other.forward:
            raise DFTTTimeRangeMethodError(
                "Cannot intersect timeranges with different directions"
            )

        if self.__fps != other.fps:
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
            return None  # No intersection

        duration = end - start if self.__forward else start - end

        return DfttTimeRange(
            start_precise_time=start,
            precise_duration=duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h and other.strict_24h,
        )

    def union(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Union operation (OR) - requires same direction and no gap"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError("Can only union with another DfttTimeRange")

        if self.__forward != other.forward:
            raise DFTTTimeRangeMethodError(
                "Cannot union timeranges with different directions"
            )

        if self.__fps != other.fps:
            raise DFTTTimeRangeFPSError("Cannot union timeranges with different FPS")

        # Check for overlap or adjacency
        if self.intersect(other) is None:
            # Check if they are adjacent
            if self.__forward:
                if not (
                    self.end_precise_time == other.start_precise_time
                    or other.end_precise_time == self.__start_precise_time
                ):
                    raise DFTTTimeRangeMethodError(
                        "Cannot union non-overlapping, non-adjacent timeranges"
                    )
            else:
                if not (
                    self.end_precise_time == other.start_precise_time
                    or other.end_precise_time == self.__start_precise_time
                ):
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

        return DfttTimeRange(
            start_precise_time=start,
            precise_duration=duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h and other.strict_24h,
        )

    def add(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Add durations - direction sensitive"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError("Can only add another DfttTimeRange")

        if self.__fps != other.fps:
            raise DFTTTimeRangeFPSError("Cannot add timeranges with different FPS")

        # Direction sensitive addition
        if self.__forward == other.forward:
            new_duration = self.__precise_duration + other.precise_duration
        else:
            new_duration = self.__precise_duration - other.precise_duration

        if new_duration == 0:
            raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

        return DfttTimeRange(
            start_precise_time=self.__start_precise_time,
            precise_duration=new_duration,
            forward=self.__forward,
            fps=self.__fps,
            strict_24h=self.__strict_24h,
        )

    def subtract(self, other: "DfttTimeRange") -> "DfttTimeRange":
        """Subtract durations - direction sensitive"""
        if not isinstance(other, DfttTimeRange):
            raise DFTTTimeRangeTypeError("Can only subtract another DfttTimeRange")

        if self.__fps != other.fps:
            raise DFTTTimeRangeFPSError("Cannot subtract timeranges with different FPS")

        # Direction sensitive subtraction
        if self.__forward == other.forward:
            new_duration = self.__precise_duration - other.precise_duration
        else:
            new_duration = self.__precise_duration + other.precise_duration

        if new_duration == 0:
            raise DFTTTimeRangeValueError("Cannot create zero-length timerange")

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
