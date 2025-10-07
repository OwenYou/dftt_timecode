import pytest
from fractions import Fraction
from dftt_timecode import DfttTimecode
from dftt_timecode.core.dftt_timerange import DfttTimeRange
from dftt_timecode.error import DFTTTimeRangeValueError, DFTTTimeRangeFPSError, DFTTTimeRangeMethodError


class TestDfttTimeRangeInitialization:
    """Test timerange initialization with different methods"""
    
    def test_init_with_timecodes(self):
        """Test initialization with start and end timecodes"""
        start = DfttTimecode('00:00:00:00', fps=24)
        end = DfttTimecode('00:00:01:00', fps=24)
        tr = DfttTimeRange(start, end)
        
        assert tr.fps == 24
        assert tr.forward == True
        assert tr.duration == 1.0
        assert tr.framecount == 24
        
    def test_init_with_mixed_types(self):
        """Test initialization with mixed timecode and other types"""
        start = DfttTimecode('00:00:00:00', fps=24)
        tr = DfttTimeRange(start, 2.0)
        
        assert tr.fps == 24
        assert tr.duration == 2.0
        
    def test_init_with_precise_values(self):
        """Test initialization with precise_duration and start_precise_time"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        assert tr.duration == 5.0
        assert tr.start_precise_time == Fraction(10)
        assert tr.precise_duration == Fraction(5)
        
    def test_init_reverse_direction(self):
        """Test initialization with reverse direction"""
        start = DfttTimecode('00:00:02:00', fps=24)
        end = DfttTimecode('00:00:00:00', fps=24)
        tr = DfttTimeRange(start, end, forward=False)
        
        assert tr.forward == False
        assert tr.duration == 2.0
        
    def test_init_fps_mismatch_error(self):
        """Test error when start and end have different FPS"""
        start = DfttTimecode('00:00:00:00', fps=24)
        end = DfttTimecode('00:00:01:00', fps=30)
        
        with pytest.raises(DFTTTimeRangeFPSError):
            DfttTimeRange(start, end)
            
    def test_init_zero_duration_error(self):
        """Test error when duration is zero"""
        start = DfttTimecode('00:00:01:00', fps=24)
        end = DfttTimecode('00:00:01:00', fps=24)
        
        with pytest.raises(DFTTTimeRangeValueError):
            DfttTimeRange(start, end)
            
    def test_init_strict_24h(self):
        """Test strict 24h mode"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(86400),  # 24 hours
            fps=24,
            strict_24h=True
        )
        
        assert tr.strict_24h == True
        assert tr.duration == 86400
        
    def test_init_strict_24h_exceeded_error(self):
        """Test error when duration exceeds 24h in strict mode"""
        with pytest.raises(DFTTTimeRangeValueError):
            DfttTimeRange(
                start_precise_time=Fraction(0),
                precise_duration=Fraction(86401),  # > 24 hours
                fps=24,
                strict_24h=True
            )


class TestDfttTimeRangeProperties:
    """Test timerange properties"""
    
    def test_basic_properties(self):
        """Test basic property access"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=25,
            forward=False
        )
        
        assert tr.fps == 25
        assert tr.forward == False
        assert tr.strict_24h == False
        assert tr.precise_duration == Fraction(5)
        assert tr.start_precise_time == Fraction(10)
        
    def test_end_precise_time_forward(self):
        """Test end_precise_time calculation for forward direction"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            forward=True
        )
        
        assert tr.end_precise_time == Fraction(15)
        
    def test_end_precise_time_reverse(self):
        """Test end_precise_time calculation for reverse direction"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            forward=False
        )
        
        assert tr.end_precise_time == Fraction(5)
        
    def test_duration_property(self):
        """Test duration property returns absolute value"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(-5),
            forward=False
        )
        
        assert tr.duration == 5.0
        
    def test_framecount_property(self):
        """Test framecount calculation"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(2),
            fps=24
        )
        
        assert tr.framecount == 48  # 2 seconds * 24 fps
        
    def test_start_end_timecode_properties(self):
        """Test start and end timecode properties"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(1),
            precise_duration=Fraction(2),
            fps=24
        )
        
        start_tc = tr.start
        end_tc = tr.end
        
        assert isinstance(start_tc, DfttTimecode)
        assert isinstance(end_tc, DfttTimecode)
        assert start_tc.timestamp == 1.0
        assert end_tc.timestamp == 3.0


class TestDfttTimeRangeCoreOperations:
    """Test core timerange operations"""
    
    def test_offset_with_number(self):
        """Test offset with numeric value"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        offset_tr = tr.offset(2.0)
        
        assert offset_tr.start_precise_time == Fraction(12)
        assert offset_tr.precise_duration == Fraction(5)
        assert offset_tr.fps == 24
        
    def test_offset_with_timecode(self):
        """Test offset with timecode"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        offset_tc = DfttTimecode('00:00:02:00', fps=24)
        offset_tr = tr.offset(offset_tc)
        
        assert offset_tr.start_precise_time == Fraction(12)  # 10 + 2
        
    def test_extend_positive(self):
        """Test extending duration"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        extended_tr = tr.extend(2)
        
        assert extended_tr.start_precise_time == Fraction(10)
        assert extended_tr.precise_duration == Fraction(7)
        
    def test_extend_negative(self):
        """Test extending with negative value (shortening)"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        extended_tr = tr.extend(-2)
        
        assert extended_tr.start_precise_time == Fraction(10)
        assert extended_tr.precise_duration == Fraction(3)
        
    def test_extend_to_zero_error(self):
        """Test error when extending to zero duration"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        with pytest.raises(DFTTTimeRangeValueError):
            tr.extend(-5)
            
    def test_shorten(self):
        """Test shortening duration"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        shortened_tr = tr.shorten(2)
        
        assert shortened_tr.start_precise_time == Fraction(10)
        assert shortened_tr.precise_duration == Fraction(3)
        
    def test_reverse(self):
        """Test reversing direction"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        reversed_tr = tr.reverse()
        
        assert reversed_tr.start_precise_time == Fraction(15)  # original end
        assert reversed_tr.precise_duration == Fraction(5)
        assert reversed_tr.forward == False
        
    def test_retime_factor(self):
        """Test retime with factor"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(4),
            fps=24
        )
        
        retimed_tr = tr.retime(0.5)
        
        assert retimed_tr.start_precise_time == Fraction(10)
        assert retimed_tr.precise_duration == Fraction(2)
        
    def test_retime_zero_error(self):
        """Test error when retime factor is zero"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(4),
            fps=24
        )
        
        with pytest.raises(DFTTTimeRangeValueError):
            tr.retime(0)
            
    def test_separate_into_parts(self):
        """Test separating timerange into parts"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(6),
            fps=24
        )
        
        parts = tr.separate(3)
        
        assert len(parts) == 3
        assert all(isinstance(part, DfttTimeRange) for part in parts)
        assert all(part.precise_duration == Fraction(2) for part in parts)
        assert parts[0].start_precise_time == Fraction(10)
        assert parts[1].start_precise_time == Fraction(12)
        assert parts[2].start_precise_time == Fraction(14)
        
    def test_separate_too_few_parts_error(self):
        """Test error when separating into too few parts"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(6),
            fps=24
        )
        
        with pytest.raises(DFTTTimeRangeValueError):
            tr.separate(1)


class TestDfttTimeRangeContains:
    """Test contains functionality"""
    
    def test_contains_timecode_forward(self):
        """Test contains with timecode in forward direction"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        tc_inside = DfttTimecode(12.0, fps=24)
        tc_outside = DfttTimecode(16.0, fps=24)
        
        assert tr.contains(tc_inside) == True
        assert tr.contains(tc_outside) == False
        
    def test_contains_timecode_reverse(self):
        """Test contains with timecode in reverse direction"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=False
        )
        
        tc_inside = DfttTimecode(8.0, fps=24)  # between 5 and 10
        tc_outside = DfttTimecode(12.0, fps=24)
        
        assert tr.contains(tc_inside) == True
        assert tr.contains(tc_outside) == False
        
    def test_contains_timerange(self):
        """Test contains with another timerange"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(10),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(12),
            precise_duration=Fraction(2),
            fps=24
        )
        
        assert tr1.contains(tr2) == True
        assert tr2.contains(tr1) == False
        
    def test_contains_string_input(self):
        """Test contains with string input"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        assert tr.contains('12.0s') == True
        assert tr.contains('16.0s') == False


class TestDfttTimeRangeOperations:
    """Test operations between timeranges"""
    
    def test_intersect_overlapping(self):
        """Test intersection of overlapping timeranges"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(10),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(10),
            fps=24
        )
        
        intersection = tr1.intersect(tr2)
        
        assert intersection is not None
        assert intersection.start_precise_time == Fraction(15)
        assert intersection.precise_duration == Fraction(5)
        
    def test_intersect_non_overlapping(self):
        """Test intersection of non-overlapping timeranges"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(5),
            fps=24
        )
        
        intersection = tr1.intersect(tr2)
        
        assert intersection is None
        
    def test_intersect_different_direction_error(self):
        """Test error when intersecting different directions"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(5),
            fps=24,
            forward=False
        )
        
        with pytest.raises(DFTTTimeRangeMethodError):
            tr1.intersect(tr2)
            
    def test_union_adjacent(self):
        """Test union of adjacent timeranges"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(5),
            fps=24
        )
        
        union = tr1.union(tr2)
        
        assert union.start_precise_time == Fraction(10)
        assert union.precise_duration == Fraction(10)
        
    def test_union_overlapping(self):
        """Test union of overlapping timeranges"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(10),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(10),
            fps=24
        )
        
        union = tr1.union(tr2)
        
        assert union.start_precise_time == Fraction(10)
        assert union.precise_duration == Fraction(15)
        
    def test_add_same_direction(self):
        """Test adding timeranges with same direction"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(3),
            fps=24,
            forward=True
        )
        
        result = tr1.add(tr2)
        
        assert result.start_precise_time == Fraction(10)
        assert result.precise_duration == Fraction(8)
        
    def test_add_different_direction(self):
        """Test adding timeranges with different directions"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(3),
            fps=24,
            forward=False
        )
        
        result = tr1.add(tr2)
        
        assert result.start_precise_time == Fraction(10)
        assert result.precise_duration == Fraction(2)  # 5 - 3
        
    def test_subtract_same_direction(self):
        """Test subtracting timeranges with same direction"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24,
            forward=True
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(3),
            fps=24,
            forward=True
        )
        
        result = tr1.subtract(tr2)
        
        assert result.start_precise_time == Fraction(10)
        assert result.precise_duration == Fraction(2)  # 5 - 3


class TestDfttTimeRangeMagicMethods:
    """Test magic methods and operators"""
    
    def test_str_representation(self):
        """Test string representation"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        str_repr = str(tr)
        assert 'DfttTimeRange' in str_repr
        assert 'fps=24' in str_repr
        
    def test_len(self):
        """Test len() returns framecount"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(2),
            fps=24
        )
        
        assert len(tr) == 48
        
    def test_contains_magic_method(self):
        """Test __contains__ magic method"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tc = DfttTimecode(12.0, fps=24)
        
        assert tc in tr
        
    def test_iteration(self):
        """Test iteration through timerange"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(1),  # 1 second
            fps=2  # 2 fps for easier testing
        )
        
        timecodes = list(tr)
        
        assert len(timecodes) == 2  # 1 second * 2 fps
        assert all(isinstance(tc, DfttTimecode) for tc in timecodes)
        
    def test_add_operator_with_timerange(self):
        """Test + operator with timerange"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(3),
            fps=24
        )
        
        result = tr1 + tr2
        
        assert result.precise_duration == Fraction(8)
        
    def test_add_operator_with_offset(self):
        """Test + operator with numeric offset"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        result = tr + 2.0
        
        assert result.start_precise_time == Fraction(12)
        
    def test_sub_operator_with_timerange(self):
        """Test - operator with timerange"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(20),
            precise_duration=Fraction(3),
            fps=24
        )
        
        result = tr1 - tr2
        
        assert result.precise_duration == Fraction(2)
        
    def test_mul_operator(self):
        """Test * operator for retime"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(4),
            fps=24
        )
        
        result = tr * 2
        
        assert result.precise_duration == Fraction(8)
        
    def test_truediv_operator(self):
        """Test / operator for retime"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(4),
            fps=24
        )
        
        result = tr / 2
        
        assert result.precise_duration == Fraction(2)
        
    def test_and_operator(self):
        """Test & operator for intersection"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(10),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(10),
            fps=24
        )
        
        result = tr1 & tr2
        
        assert result is not None
        assert result.precise_duration == Fraction(5)
        
    def test_or_operator(self):
        """Test | operator for union"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(5),
            fps=24
        )
        
        result = tr1 | tr2
        
        assert result.precise_duration == Fraction(10)
        
    def test_equality_comparison(self):
        """Test equality comparison"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr3 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(6),
            fps=24
        )
        
        assert tr1 == tr2
        assert tr1 != tr3
        
    def test_comparison_operators(self):
        """Test comparison operators"""
        tr1 = DfttTimeRange(
            start_precise_time=Fraction(10),
            precise_duration=Fraction(5),
            fps=24
        )
        
        tr2 = DfttTimeRange(
            start_precise_time=Fraction(15),
            precise_duration=Fraction(5),
            fps=24
        )
        
        assert tr1 < tr2
        assert tr1 <= tr2
        assert tr2 > tr1
        assert tr2 >= tr1


class TestDfttTimeRangeEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_midnight_crossing_strict_mode(self):
        """Test midnight crossing in strict mode"""
        start = DfttTimecode('23:59:59:00', fps=24)
        end = DfttTimecode('00:00:01:00', fps=24)
        
        tr = DfttTimeRange(start, end, strict_24h=True)
        
        # Should handle midnight crossing correctly
        assert tr.duration == 2.0  # 1 second before + 1 second after midnight
        
    def test_very_small_duration(self):
        """Test very small duration handling"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(1, 1000),  # 1ms
            fps=24
        )
        
        assert tr.duration == 0.001
        
    def test_high_fps_precision(self):
        """Test high FPS precision"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(1),
            fps=999.99  # high fps
        )
        
        assert tr.framecount == 1000  # approximately
        
    def test_fractional_fps(self):
        """Test fractional FPS"""
        tr = DfttTimeRange(
            start_precise_time=Fraction(0),
            precise_duration=Fraction(2),
            fps=23.976  # 23.976 fps
        )
        
        expected_frames = int(round(2 * 23.976))
        assert tr.framecount == expected_frames


if __name__ == '__main__':
    pytest.main([__file__, '-v'])