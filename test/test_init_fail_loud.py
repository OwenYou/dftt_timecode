"""Tests locking in fail-loud initialization behavior for DfttTimecode and DfttTimeRange.

These tests guard against silent fallbacks on partial construction. Construction
is forced via __new__ + a bare __init__ call inside a pytest.raises block so we
can inspect the half-built object. Real callers never see such an object, but
class-level defaults made silent corruption possible if anyone caught the
exception and continued using the partially constructed instance.
"""

import pytest

from dftt_timecode import DfttTimecode, DfttTimeRange
from dftt_timecode.error import DFTTTimecodeTypeError, DFTTTimeRangeValueError


class TestDfttTimecodePartialInitFailsLoud:
    """If __init__ raises mid-way, accessing state attributes must raise
    AttributeError instead of silently returning a class-level zero default."""

    def test_string_init_failure_does_not_leave_zero_precise_time(self):
        instance = DfttTimecode.__new__(DfttTimecode)
        with pytest.raises(DFTTTimecodeTypeError):
            instance.__init__("garbage-not-a-timecode", "auto", 24.0, False, True)
        with pytest.raises(AttributeError):
            _ = instance.precise_timestamp

    def test_string_init_failure_does_not_leave_zero_timestamp(self):
        instance = DfttTimecode.__new__(DfttTimecode)
        with pytest.raises(DFTTTimecodeTypeError):
            instance.__init__("garbage-not-a-timecode", "auto", 24.0, False, True)
        with pytest.raises(AttributeError):
            _ = instance.timestamp

    def test_string_init_failure_does_not_leave_zero_framecount(self):
        instance = DfttTimecode.__new__(DfttTimecode)
        with pytest.raises(DFTTTimecodeTypeError):
            instance.__init__("garbage-not-a-timecode", "auto", 24.0, False, True)
        with pytest.raises(AttributeError):
            _ = instance.framecount

    def test_fresh_new_object_has_no_state(self):
        """An object returned by __new__ but never __init__'d has no instance
        attributes at all. Property access must raise AttributeError."""
        instance = DfttTimecode.__new__(DfttTimecode)
        with pytest.raises(AttributeError):
            _ = instance.fps
        with pytest.raises(AttributeError):
            _ = instance.precise_timestamp


class TestDfttTimecodeBaseDispatchRejection:
    """Unsupported value types must raise DFTTTimecodeTypeError, not bare TypeError."""

    def test_unsupported_dict_raises_dftt_error(self):
        with pytest.raises(DFTTTimecodeTypeError):
            DfttTimecode({"not": "supported"})

    def test_unsupported_type_message_names_the_type(self):
        with pytest.raises(DFTTTimecodeTypeError) as excinfo:
            DfttTimecode({"not": "supported"})
        assert "dict" in str(excinfo.value)


class TestDfttTimecodePassthroughRemoved:
    """The DfttTimecode(existing_tc) passthrough (CHANGELOG 0.0.10) is removed
    in 1.0.0b4. Constructing from an existing DfttTimecode must now raise
    DFTTTimecodeTypeError. Callers that want to reuse an instance should pass
    it directly; callers that want a copy should construct from a primitive
    representation (precise_timestamp, framecount, or a string form)."""

    def test_constructing_from_existing_dftt_timecode_raises(self):
        original = DfttTimecode("01:00:00:00", "auto", fps=24, drop_frame=False, strict=True)
        with pytest.raises(DFTTTimecodeTypeError):
            DfttTimecode(original)

    def test_passthrough_removal_message_names_dftttimecode(self):
        original = DfttTimecode("01:00:00:00", "auto", fps=24, drop_frame=False, strict=True)
        with pytest.raises(DFTTTimecodeTypeError) as excinfo:
            DfttTimecode(original)
        assert "DfttTimecode" in str(excinfo.value)


class TestDfttTimeRangePartialInitFailsLoud:
    """DfttTimeRange has no class-level state defaults. Verify partial init
    raises AttributeError on subsequent state access, locking in the invariant."""

    def test_invalid_construction_raises(self):
        with pytest.raises(DFTTTimeRangeValueError):
            DfttTimeRange()  # neither tc pair nor precise pair provided

    def test_partial_init_object_has_no_duration(self):
        instance = DfttTimeRange.__new__(DfttTimeRange)
        with pytest.raises(DFTTTimeRangeValueError):
            instance.__init__()
        with pytest.raises(AttributeError):
            _ = instance.precise_duration
