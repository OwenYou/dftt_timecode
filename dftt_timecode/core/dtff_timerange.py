from copy import deepcopy
from fractions import Fraction

from dftt_timecode.core.dftt_timecode import DfttTimecode
from dftt_timecode.error import DFTTError, DFTTTimeRangeFPSError, DFTTTimeRangeMethodError, DFTTTimeRangeTypeError, DFTTTimeRangeValueError


class DfttTimeRange:
    TIME_24H = 86400

    __start = DfttTimecode(0.0)
    __end = DfttTimecode(1.0)
    __fps = 24.0
    __forward = True
    __strict_24h = False
    __midnight = False

    def __init__(self, start_tc, end_tc, forward: bool=True, fps=24.0):
        self.__forward = forward
        if isinstance(start_tc, DfttTimecode) and isinstance(end_tc, DfttTimecode):
            if start_tc.fps != end_tc.fps:
                raise DFTTTimeRangeFPSError

            if start_tc.timestamp == end_tc.timestamp:
                raise DFTTTimeRangeValueError(
                    'Time range cannot be zero-length!')

            self.__start = start_tc
            self.__end = end_tc
            self.__fps = start_tc.fps
        elif isinstance(start_tc, DfttTimecode):
            try:
                end_tc = DfttTimecode(end_tc, fps=start_tc.fps, drop_frame=start_tc.is_drop_frame,
                                      strict=start_tc.is_strict)
            except DFTTError:
                raise DFTTTimeRangeTypeError
            else:
                if start_tc.timestamp != end_tc.timestamp:
                    self.__start = start_tc
                    self.__end = end_tc
                    self.__fps = start_tc.fps
                else:
                    raise DFTTTimeRangeValueError
        elif isinstance(end_tc, DfttTimecode):
            try:
                start_tc = DfttTimecode(start_tc, fps=end_tc.fps, drop_frame=end_tc.is_drop_frame,
                                        strict=end_tc.is_strict)
            except DFTTError:
                raise DFTTTimeRangeTypeError
            else:
                if start_tc.timestamp != end_tc.timestamp:
                    self.__start = start_tc
                    self.__end = end_tc
                    self.__fps = start_tc.fps
                else:
                    raise DFTTTimeRangeValueError
        else:
            try:
                start_tc = DfttTimecode(start_tc, fps=fps)
                end_tc = DfttTimecode(end_tc, fps=fps)
            except DFTTError:
                raise DFTTTimeRangeTypeError
            else:
                if start_tc.timestamp == end_tc.timestamp:
                    raise DFTTTimeRangeValueError
                self.__start = start_tc
                self.__end = end_tc
                self.__fps = fps

        if self.__start.is_strict and self.__end.is_strict:
            self.__strict_24h = True

        if (self.__end < self.__start and self.__forward is True) or (self.__end > self.__start and self.__forward is False):
            self.__midnight = True

        # def _auto_forward() -> bool:
        #     if self.__start > self.__end:
        #         return False
        #     elif self.__start < self.__end:
        #         return True

        # self.__forward = forward if forward is not None else _auto_forward()

    @property
    def duration(self) -> float:
        # 使用precise_timestamp属性相加减计算duration
        # 避免反向Range(Forward == False)并且strict == True时
        # __start-__end的precise_timestamp被mapping到(0.0,86400.0)内的问题
        if self.__strict_24h is True and self.__midnight is True:
            return float(self.TIME_24H)-abs(float(self.__end.precise_timestamp - self.__start.precise_timestamp))
        else:
            return abs(float(self.__end.precise_timestamp - self.__start.precise_timestamp))

    @property
    def framecount(self) -> int:
        # 使用precise_timestamp属性相加减计算duration
        # 避免反向Range(Forward == False)并且strict == True时
        # __start-__end的precise_timestamp被mapping到(0.0,86400.0*fps)内的问题
        if self.__strict_24h is True and self.__midnight is True:
            return int(round(self.TIME_24H*self.__fps))-abs(int(self.__end.framecount - self.__start.framecount))
        else:
            return abs(int(self.__end.framecount - self.__start.framecount))

    @property
    def start(self) -> DfttTimecode:
        return deepcopy(self.__start)

    @property
    def end(self) -> DfttTimecode:
        return deepcopy(self.__end)

    def offset(self, offset_value):
        try:
            self.__start += offset_value
            self.__end += offset_value
        except DFTTError:
            raise DFTTTimeRangeMethodError

    def align_to(self, time, head_or_tail=True):
        # TODO
        pass

    def handle(self, head, tail=None):
        tail = head if tail is None else tail
        try:
            self.__start -= head
            self.__end += tail
        except DFTTError:
            raise DFTTTimeRangeMethodError
        if self.__start == self.__end:
            raise DFTTTimeRangeValueError
        else:
            pass

    def retime(self, retime_factor):
        if type(retime_factor) in (int, float, Fraction):
            temp_duration = (self.__end - self.__start).precise_timestamp
            self.__end = self.__start + temp_duration / retime_factor
        else:
            raise DFTTTimeRangeTypeError

    def cut(self, cut_point):
        try:
            if cut_point in self:
                return [DfttTimeRange(self.__start, cut_point), DfttTimeRange(self.__end, cut_point)]
            else:
                return [self]
        except DFTTError:
            raise DFTTTimeRangeTypeError

    def iter(self, step=1):
        return self.__iter__(step)

    def overlap_with(self, other):
        if isinstance(other, DfttTimeRange):
            if self.__start < other.__start:
                print(1)
                return self.__end - other.__start > 0 and other.__start - self.__start > 0
            else:
                return other.__end - self.__start > 0 and self.__start - other.__start > 0
        else:
            raise DFTTTimeRangeTypeError('Other NOT DfttTimeRange')

    def seperate_with(self, other):
        if isinstance(other, DfttTimeRange):
            # TODO
            pass

    def __str__(self) -> str:
        return f"DfttTimeRange({str(self.__start)},{str(self.__end)},fps={self.__fps})"

    def __repr__(self):
        output_str1 = '{}{}, {}{}, {}{:.02f} {}, {}'.format('Timecode:',
                                                            self.__start.timecode_output(
                                                                self.__start.type),
                                                            'Type:', self.__start.type, 'FPS:', float(
                                                                self.__start.fps),
                                                            'DF' if self.__start.is_drop_frame is True else 'NDF',
                                                            'Strict' if self.__start.is_strict is True else 'Non-Strict')
        output_str2 = '{}{}, {}{}, {}{:.02f} {}, {}'.format('Timecode:',
                                                            self.__end.timecode_output(
                                                                self.__end.type),
                                                            'Type:', self.__end.type, 'FPS:', float(
                                                                self.__end.fps),
                                                            'DF' if self.__end.is_drop_frame is True else 'NDF',
                                                            'Strict' if self.__end.is_strict is True else 'Non-Strict')
        return '<DfttTimeRange>\n|{}{}|\n|{}{}|'.format('Start:', output_str1, 'End:', output_str2)

    def __len__(self):
        return self.framecount

    # TODO forward compatibility
    def __contains__(self, item):
        if isinstance(item, DfttTimecode):
            # return self.__start <= item <= self.__end
            return self.__end - item > 0 and item - self.__start > 0
        elif isinstance(item, DfttTimeRange):
            return self.__end - item.__start > 0 and item.__start - self.__start > 0 and\
                self.__end - item.__end > 0 and item.__end - self.__start > 0
        else:
            try:
                return self.__end - item > 0 and item - self.__start > 0
            except DFTTError:
                raise DFTTTimeRangeTypeError

    def __iter__(self, step=1):
        tc = self.start
        while tc <= self.__end:
            yield tc
            tc += step

    def __lshift__(self, other):
        self.handle(head=other, tail=0)

    def __rshift__(self, other):
        self.handle(head=0, tail=other)
