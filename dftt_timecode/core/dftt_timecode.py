"""
Core timecode class implementation for DFTT Timecode library.

This module contains the main DfttTimecode class which provides comprehensive
timecode functionality for film and television production workflows.
"""

import logging
from fractions import Fraction
from functools import singledispatchmethod
from math import ceil, floor
from typing import Literal, TypeAlias, Union

from dftt_timecode.error import (
    DFTTTimecodeInitializationError,
    DFTTTimecodeOperatorError,
    DFTTTimecodeTypeError,
    DFTTTimecodeValueError,
)
from dftt_timecode.pattern import (
    DLP_REGEX,
    FCPX_REGEX,
    FFMPEG_REGEX,
    FRAME_REGEX,
    SMPTE_DF_REGEX,
    SMPTE_NDF_REGEX,
    SMPTE_REGEX,
    SRT_REGEX,
    TIME_REGEX,
)

# logging.basicConfig(filename='dftt_timecode_log.txt',
#                     filemode='w',
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%Y-%m-%d %a %H:%M:%S',
#                     level=logging.DEBUG)
#set up logger
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter=logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d-%(funcName)s()] %(message)s')

stream_handler=logging.StreamHandler()
stream_handler.setFormatter(formatter)

# file_handler=logging.FileHandler('dftt_timecode_log.txt',filemode='w')
# file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

TimecodeType: TypeAlias = Literal['smpte', 'srt', 'dlp', 'ffmpeg', 'fcpx', 'frame', 'time', 'auto']
"""Type alias for supported timecode format types.

Available formats:
    - ``'smpte'``: SMPTE format (01:23:45:12 or 01:23:45;12 for drop-frame)
    - ``'srt'``: SubRip subtitle format (01:23:45,678)
    - ``'dlp'``: DLP Cinema format (01:23:45:102)
    - ``'ffmpeg'``: FFmpeg format (01:23:45.67)
    - ``'fcpx'``: Final Cut Pro X format (1/24s)
    - ``'frame'``: Frame count format (1234f)
    - ``'time'``: Timestamp in seconds (1234.5s)
    - ``'auto'``: Automatic format detection based on input pattern
"""


class DfttTimecode:
    """High-precision timecode class for film and television production.

    DfttTimecode provides frame-accurate timecode representation with support for multiple
    professional formats, high frame rates (0.01-999.99 fps), drop-frame compensation,
    and comprehensive arithmetic operations.

    The class uses :class:`fractions.Fraction` internally for precise timestamp calculations,
    ensuring accuracy even with complex operations and format conversions.

    Args:
        timecode_value: The timecode value in various supported formats:
            - str: Timecode string (e.g., '01:00:00:00', '01:00:00,000')
            - int: Frame count (with timecode_type='frame') or seconds (with timecode_type='time')
            - float: Timestamp in seconds
            - Fraction: Precise timestamp as rational number
            - tuple/list: Two-element [numerator, denominator] for rational time
            - DfttTimecode: Returns the same instance (no copy)
        timecode_type: Format type of the timecode value. Use 'auto' for automatic detection.
            See :data:`TimecodeType` for available formats. Defaults to 'auto'.
        fps: Frame rate in frames per second. Supports 0.01-999.99 fps. Defaults to 24.0.
        drop_frame: Enable drop-frame compensation for NTSC-compatible frame rates
            (29.97, 59.94, 119.88 fps and their multiples). Defaults to False.
        strict: Enable 24-hour wraparound mode. When True, timecodes automatically cycle
            within 0-24 hour range (e.g., 25:00:00:00 becomes 01:00:00:00). Defaults to True.

    Attributes:
        type (str): Current timecode format type
        fps (float): Frame rate in frames per second
        is_drop_frame (bool): Whether drop-frame compensation is enabled
        is_strict (bool): Whether 24-hour strict mode is enabled
        framecount (int): Total frame count from zero
        timestamp (float): Total seconds from zero
        precise_timestamp (Fraction): High-precision timestamp as Fraction

    Raises:
        DFTTTimecodeInitializationError: When initialization parameters are incompatible
        DFTTTimecodeTypeError: When timecode type doesn't match the value format
        DFTTTimecodeValueError: When timecode value is invalid for the given parameters

    Examples:
        Create from SMPTE timecode string::

            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> print(tc)
            01:00:00:00

        Create with automatic format detection::

            >>> tc = DfttTimecode('01:00:00,000', 'auto', fps=25)
            >>> print(tc.type)
            srt

        Create from frame count::

            >>> tc = DfttTimecode(1000, 'frame', fps=24)
            >>> print(tc.timecode_output('smpte'))
            00:00:41:16

        Create with drop-frame compensation::

            >>> tc = DfttTimecode('01:00:00;00', fps=29.97, drop_frame=True)
            >>> print(tc.is_drop_frame)
            True

        Arithmetic operations::

            >>> tc1 = DfttTimecode('01:00:00:00', fps=24)
            >>> tc2 = tc1 + 100  # Add 100 frames
            >>> print(tc2)
            01:00:04:04
            >>> tc3 = tc1 + 3.5  # Add 3.5 seconds
            >>> print(tc3)
            01:00:03:12

        Format conversion::

            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> print(tc.timecode_output('srt'))
            01:00:00,000
            >>> print(tc.timecode_output('ffmpeg'))
            01:00:00.00

    Note:
        - Timecode objects are immutable. All operations return new instances.
        - The internal timestamp uses :class:`fractions.Fraction` for maximum precision.
        - Drop-frame compensation is automatically validated against frame rate.
        - Negative timecodes are supported with a leading minus sign.

    See Also:
        - :class:`DfttTimeRange`: For working with time intervals
        - :mod:`dftt_timecode.pattern`: Regex patterns for format validation
        - :mod:`dftt_timecode.error`: Custom exception classes
    """
    __type = 'time'
    __fps = 24.0  # 帧率
    __nominal_fps = 24  # 名义帧率（无小数,进一法取整）
    __drop_frame = False  # 是否丢帧Dropframe（True为丢帧，False为不丢帧）
    __strict = True  # 严格模式，默认为真，在该模式下不允许超出24或小于0的时码，将自动平移至0-24范围内，例如-1小时即为23小时，25小时即为1小时
    __precise_time = Fraction(0)  # 精准时间戳，是所有时码类对象的工作基础

    def __new__(cls, timecode_value=0, timecode_type='auto', fps=24.0, drop_frame=False, strict=True):
        if isinstance(timecode_value, DfttTimecode):
            return timecode_value
        else:
            return super(DfttTimecode, cls).__new__(cls)
        
    def __validate_drop_frame(self, drop_frame: bool, fps: float) -> bool:
        if round(fps, 2) % 29.97 == 0:
            # FPS为29.97以及倍数时候，尊重drop_frame参数(for 29.97/59.94/119.88 NDF)
            return False if not drop_frame else True
        else:
            return round(self.fps, 2) % 23.98 == 0

    def __detect_timecode_type(self,timecode_value)->TimecodeType:
        if SMPTE_NDF_REGEX.match(timecode_value):  # SMPTE NDF 强制DF为False
            if self.__drop_frame:
                raise DFTTTimecodeInitializationError(f'Init Timecode Failed: Timecode value [{timecode_value}] DONOT match drop_frame status [{self.__drop_frame}]! Check input.')
            return 'smpte'

        elif SMPTE_DF_REGEX.match(timecode_value):
            
            # 判断丢帧状态与帧率是否匹配 不匹配则强制转换
            if not self.__drop_frame:
                raise DFTTTimecodeInitializationError(f'Init Timecode Failed: Timecode value [{timecode_value}] DONOT match drop_frame status [{self.__drop_frame}]! Check input.')
            return 'smpte'
        elif SRT_REGEX.match(timecode_value):
            return 'srt'
        elif FFMPEG_REGEX.match(timecode_value):
            return 'ffmpeg'
        elif FCPX_REGEX.match(timecode_value):
            return  'fcpx'
        elif FRAME_REGEX.match(timecode_value):
            return  'frame'
        elif TIME_REGEX.match(timecode_value):
            return  'time'
        
    def __apply_strict(self) -> None:
        """Apply 24h wraparound if strict mode enabled"""
        if self.__strict:
            self.__precise_time %= 86400
            
        
    def __init_smpte(self, timecode_value: str,minus_flag:bool):
        if not SMPTE_REGEX.match(timecode_value):  # 判断输入是否符合
                logger.error(
                    f'Timecode type [smpte] DONOT match input value [{timecode_value}]! Check input.')
                raise DFTTTimecodeTypeError
        temp_timecode_list = [int(x) if x else 0 for x in SMPTE_REGEX.match(
            timecode_value).groups()]  # 正则取值
        hh,mm,ss,ff = temp_timecode_list
        if ff > self.__nominal_fps - 1:  # 判断输入帧号在当前帧率下是否合法
            logger.error(
                f'This timecode: [{timecode_value}] is illegal under given params, check your input!')
            raise DFTTTimecodeValueError

        if not self.__drop_frame:  # 时码丢帧处理逻辑
            frame_index = ff + self.__nominal_fps * \
                (ss + mm * 60 + hh * 3600)
        else:
            drop_per_min = self.__nominal_fps / 30 * 2
            # 检查是否有DF下不合法的帧号
            if mm % 10 != 0 and ss == 0 and ff in (0, drop_per_min - 1):
                logger.error(
                    f'This timecode: [{timecode_value}] is illegal under given params, check your input!')
                raise DFTTTimecodeValueError
            else:
                total_minutes = 60 * hh + mm
                frame_index = (hh * 3600 + mm * 60 + ss) * self.__nominal_fps + ff - (
                    self.__nominal_fps / 30) * 2 * (
                    # 逢十分钟不丢帧 http://andrewduncan.net/timecodes/
                    total_minutes - total_minutes // 10)
        if self.__strict:  # strict输入逻辑
            frame_index = frame_index % (self.__fps * 86400) if self.__drop_frame else frame_index % (
                self.__nominal_fps * 86400)  # 对于DF时码来说，严格处理取真实FPS的模，对于NDF时码，则取名义FPS的模
            
        if minus_flag:
            frame_index = -frame_index
        self.__precise_time = Fraction(
            frame_index / self.__fps)  # 时间戳=帧号/帧率
    
    def __init_srt(self, timecode_value: str,minus_flag:bool):
        if not SRT_REGEX.match(timecode_value):  # 判断输入是否符合SRT类型
            logger.error(
                f'Timecode type [srt] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        
        temp_timecode_list = [
            int(x) if x else 0 for x in SRT_REGEX.match(timecode_value).groups()]
        # 由于SRT格式本身不存在帧率，将为SRT赋予默认帧率和丢帧状态
        logger.info(f'SRT timecode framerate {self.__fps}, DF={self.__drop_frame} assigned')
        hh,mm,ss,sub_sec = temp_timecode_list
        
        self.__precise_time = Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 1000)
        if minus_flag:
            self.__precise_time = -self.__precise_time
            
        self.__apply_strict()
        
    
    def __init_dlp(self, timecode_value: str, minus_flag: bool):
        if not DLP_REGEX.match(timecode_value):
            logger.error(
                f'Timecode type [dlp] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        temp_timecode_list = [
            int(x) if x else 0 for x in DLP_REGEX.match(timecode_value).groups()]
        # 由于DLP不存在帧率，将为DLP赋予默认帧率和丢帧状态
        logger.info(f'DLP timecode framerate {self.__fps}, DF={self.__drop_frame} assigned')
        hh, mm, ss, sub_sec = temp_timecode_list
        # dlp每秒共250个子帧 即4ms一个
        # 详见https://interop-docs.cinepedia.com/Reference_Documents/CineCanvas(tm)_RevC.pdf 第17页 “TimeIn”部分

        self.__precise_time = Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 250)
        if minus_flag:
            self.__precise_time = -self.__precise_time
        self.__apply_strict()

        
    def __init_ffmpeg(self, timecode_value: str,minus_flag:bool):
        if not FFMPEG_REGEX.match(timecode_value):
            logger.error(f'Timecode type [ffmpeg] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        temp_timecode_list = [
            int(x) if x else 0 for x in FFMPEG_REGEX.match(timecode_value).groups()]
        hh,mm,ss,sub_sec = temp_timecode_list
        self.__precise_time = Fraction(hh * 3600 + mm * 60 + ss + float(f'0.{sub_sec}'))
        if minus_flag:
            self.__precise_time = -self.__precise_time
            
        self.__apply_strict()

    def __init_fcpx(self, timecode_value: str,minus_flag:bool):
        if not FCPX_REGEX.match(timecode_value):
            logger.error(f'Timecode type [fcpx] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        temp_timecode_list = [
            int(x) if x else 0 for x in FCPX_REGEX.match(timecode_value).groups()]
        self.__precise_time = Fraction(temp_timecode_list[0], temp_timecode_list[1])
        if minus_flag:
            self.__precise_time = -self.__precise_time
            
        self.__apply_strict()
    
    def __init_frame(self, timecode_value: str,minus_flag:bool):
        if not FRAME_REGEX.match(timecode_value):
            logger.error(f'Timecode type [frame] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        temp_frame_index = int(FRAME_REGEX.match(timecode_value).group(1))
        if self.__strict:  # 严格模式，对于丢帧时码而言 用实际FPS运算，对于不丢帧时码而言，使用名义FPS运算
            temp_frame_index = temp_frame_index % (
                self.__fps * 86400) if self.__drop_frame else temp_frame_index % (
                self.__nominal_fps * 86400)
        else:
            pass
        self.__precise_time = Fraction(
            temp_frame_index / self.__fps)  # 转换为内部精准时间戳
        
    def __init_time(self, timecode_value: str,minus_flag:bool):
        if not TIME_REGEX.match(timecode_value):
            logger.error(f'Timecode type [time] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        temp_timecode_value = TIME_REGEX.match(timecode_value).group(1)
        self.__precise_time = Fraction(temp_timecode_value)  # 内部时间戳直接等于输入值
        
        self.__apply_strict()
    
    def __init_common(self, timecode_type,fps,drop_frame,strict):
        self.__type = timecode_type
        self.__fps = fps
        self.__nominal_fps = ceil(fps)
        self.__drop_frame = self.__validate_drop_frame(drop_frame, fps)
        self.__strict = strict
        
    @singledispatchmethod
    def __init__(self, timecode_value, timecode_type, fps, drop_frame, strict):  # 构造函数
        raise TypeError(f"Unsupported timecode value type: {type(timecode_value)}")

    @__init__.register  # 若传入的TC值为字符串，则调用此函数
    def _(self, timecode_value: str, timecode_type:TimecodeType='auto', fps=24.0, drop_frame=None, strict=True):
        # if timecode_value[0] == '-':  # 判断首位是否为负，并为flag赋值
        #     minus_flag = True
        # else:
        #     minus_flag = False
        minus_flag= timecode_value.startswith('-')
        self.__fps = fps
        # 读入帧率取整为名义帧率便于后续计算（包括判断时码是否合法，DF/NDF逻辑等) 用进一法是因为要判断ff值是否大于fps-1
        self.__nominal_fps = ceil(fps)
        self.__drop_frame = self.__validate_drop_frame(drop_frame, fps)
        self.__strict = strict
        
        timecode_type= timecode_type if timecode_type != 'auto' else self.__detect_timecode_type(timecode_value)
        
        self.__type = timecode_type      
    
        timecode_type_handler_map={
            'smpte':self.__init_smpte,
            'srt':self.__init_srt,
            'dlp':self.__init_dlp,
            'ffmpeg':self.__init_ffmpeg,
            'fcpx':self.__init_fcpx,
            'frame':self.__init_frame,
            'time':self.__init_time
        }
        init_func=timecode_type_handler_map[timecode_type]
        if not init_func:
            raise DFTTTimecodeTypeError(f'Unknown timecode type :{timecode_type}')
        init_func(timecode_value,minus_flag)
    
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        # logging.debug(instance_success_log)
        logger.debug(instance_success_log)

    @__init__.register  # 输入为Fraction类分数，此时认为输入是时间戳，若不是，则会报错
    def _(self, timecode_value: Fraction, timecode_type='time', fps=24.0, drop_frame=False, strict=True):
        if timecode_type in ('time', 'auto'):
            self.__init_common(timecode_type,fps,drop_frame,strict)
            self.__precise_time = timecode_value  # 内部时间戳直接等于输入值
            self.__apply_strict()
        else:
            logger.error(
                f'Timecode type [{timecode_type}] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        logger.debug(instance_success_log)

    @__init__.register
    def _(self, timecode_value: int, timecode_type='frame', fps=24.0, drop_frame=False, strict=True):
        if timecode_type in ('frame', 'auto'):
            self.__init_common(timecode_type,fps,drop_frame,strict)
            temp_frame_index = timecode_value
            if self.__strict:
                temp_frame_index = temp_frame_index % (
                    self.__fps * 86400) if self.__drop_frame else temp_frame_index % (
                    self.__nominal_fps * 86400)
            self.__precise_time = Fraction(temp_frame_index / self.__fps)
            
        elif timecode_type == 'time':
            self.__init_common(timecode_type,fps,drop_frame,strict)
            self.__precise_time = timecode_value  # 内部时间戳直接等于输入值
            self.__apply_strict()
        else:
            logger.error(
                f'Timecode type [{timecode_type}] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        logger.debug(instance_success_log)

    @__init__.register
    def _(self, timecode_value: float, timecode_type='time', fps=24.0, drop_frame=False, strict=True):
        if timecode_type in ('time', 'auto'):
            self.__init_common(timecode_type,fps,drop_frame,strict)
            self.__precise_time = Fraction(timecode_value)  # 内部时间戳直接等于输入值
            self.__apply_strict()
        else:
            logger.error(
                f'Timecode type [{timecode_type}] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        logger.debug(instance_success_log)

    @__init__.register
    def _(self, timecode_value: tuple, timecode_type='time', fps=24.0, drop_frame=False, strict=True):
        if timecode_type in ('time', 'auto'):
            self.__init_common(timecode_type,fps,drop_frame,strict)
            self.__precise_time = Fraction(
                int(timecode_value[0]), int(timecode_value[1]))  # 将tuple输入视为分数
            self.__apply_strict()
        else:
            logger.error(
                f'Timecode type [{timecode_type}] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        logger.debug(instance_success_log)

    @__init__.register
    def _(self, timecode_value: list, timecode_type='time', fps=24.0, drop_frame=False, strict=True):
        if timecode_type in ('time', 'auto'):
            self.__init_common(timecode_type,fps,drop_frame,strict)
            self.__precise_time = Fraction(
                int(timecode_value[0]), int(timecode_value[1]))  # 将list输入视为分数
            self.__apply_strict()
        else:
            logger.error(
                f'Timecode type [{timecode_type}] DONOT match input value [{timecode_value}]! Check input.')
            raise DFTTTimecodeTypeError
        instance_success_log = f'value type {type(timecode_value)} Timecode instance: type={self.__type}, fps={self.__fps}, dropframe={self.__drop_frame}, strict={self.__strict}'
        logger.debug(instance_success_log)

    @property
    def type(self) -> str:
        """Get the current timecode format type.

        Returns:
            str: The timecode format type (e.g., 'smpte', 'srt', 'ffmpeg')

        Example:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> tc.type
            'smpte'
        """
        return self.__type

    @property
    def fps(self) -> float:
        """Get the frame rate in frames per second.

        Returns:
            float: The frame rate

        Example:
            >>> tc = DfttTimecode('01:00:00:00', fps=29.97)
            >>> tc.fps
            29.97
        """
        return self.__fps

    @property
    def is_drop_frame(self) -> bool:
        """Check if drop-frame compensation is enabled.

        Returns:
            bool: True if drop-frame mode is enabled, False otherwise

        Note:
            Drop-frame is automatically enabled for NTSC-compatible frame rates
            (29.97, 59.94, 119.88 and their multiples) when drop_frame=True.

        Example:
            >>> tc = DfttTimecode('01:00:00;00', fps=29.97, drop_frame=True)
            >>> tc.is_drop_frame
            True
        """
        return self.__drop_frame

    @property
    def is_strict(self) -> bool:
        """Check if 24-hour strict mode is enabled.

        Returns:
            bool: True if strict mode is enabled, False otherwise

        Note:
            In strict mode, timecodes automatically wrap around at 24 hours.

        Example:
            >>> tc = DfttTimecode('25:00:00:00', fps=24, strict=True)
            >>> print(tc)
            01:00:00:00
        """
        return self.__strict

    @property
    def framecount(self) -> int:
        """Get the total frame count from zero.

        Returns:
            int: The frame number (zero-indexed)

        Example:
            >>> tc = DfttTimecode('00:00:01:00', fps=24)
            >>> tc.framecount
            24
        """
        return int(self._convert_to_output_frame())

    @property
    def timestamp(self) -> float:
        """Get the timestamp in seconds from zero.

        Returns:
            float: The timestamp in seconds (rounded to 5 decimal places)

        Example:
            >>> tc = DfttTimecode('00:00:01:00', fps=24)
            >>> tc.timestamp
            1.0
        """
        return float(self._convert_to_output_time())

    @property
    def precise_timestamp(self) -> Fraction:
        """Get the high-precision timestamp as a Fraction.

        Returns:
            Fraction: The precise timestamp for exact calculations

        Note:
            This is the internal representation used for all calculations
            to maintain maximum precision.

        Example:
            >>> tc = DfttTimecode('00:00:01:00', fps=24)
            >>> tc.precise_timestamp
            Fraction(1, 1)
        """
        return self.__precise_time

    def _convert_to_output_smpte(self, output_part=0) -> str:
        minus_flag = False
        frame_index = round(self.__precise_time * self.__fps)  # 从内部时间戳计算得帧计数
        if frame_index < 0:  # 负值时，打上flag，并翻转负号
            minus_flag = True
            frame_index = -frame_index

        # 计算framecount用于输出smpte时码个部分值
        if not self.__drop_frame:  # 不丢帧
            # 对于不丢帧时码而言 framecount 为帧计数
            _nominal_framecount = frame_index
        else:  # 丢帧
            drop_per_min = self.__nominal_fps / 30 * 2  # 提前计算每分钟丢帧数量 简化后续计算
            df_framecount_10min = self.__nominal_fps * 600 - 9 * drop_per_min

            d, m = divmod(frame_index, df_framecount_10min)
            drop_frame_frame_number = frame_index + drop_per_min * 9 * d + drop_per_min * (
                # 剩余小于十分钟部分计算丢了多少帧，补偿
                ((m - drop_per_min) // (self.__nominal_fps * 60 - drop_per_min)) if m > 2 else 0)

            _nominal_framecount = drop_frame_frame_number

        def _convert_framecount_to_smpte_parts(frame_count: int, fps: int) -> tuple:
            hour, r_1 = divmod(frame_count, 60*60*fps)
            minute, r_2 = divmod(r_1, 60*fps)
            second, frame = divmod(r_2, fps)
            return int(hour), int(minute), int(second), round(frame)

        output_hh, output_mm, output_ss, output_ff = _convert_framecount_to_smpte_parts(
            _nominal_framecount, self.__nominal_fps)

        output_ff_format = '02d' if self.__fps < 100 else '03d'
        output_minus_flag = '' if not minus_flag else '-'
        output_strs = (
            f'{output_minus_flag}{output_hh:02d}',
            f'{output_mm:02d}',
            f'{output_ss:02d}',
            f'{output_ff:{output_ff_format}}')

        if output_part > len(output_strs):
            logger.warning(
                'No such part, will return the last part of timecode')
            return output_strs[-1]

        # 输出完整时码字符串
        if output_part == 0:
            main_part = ':'.join(output_strs[:3])
            # 丢帧时码的帧号前应为分号
            separator = ';' if self.__drop_frame else ':'
            output_str = f'{main_part}{separator}{output_strs[3]}'
            return output_str

        elif 1 <= output_part <= len(output_strs):
            return output_strs[output_part-1]

        else:
            raise IndexError(
                'Negtive output_part is not allowed')

    def _convert_precise_time_to_parts(self, sub_sec_multiplier: int, frame_seperator: str, sub_sec_format: str) -> tuple[str, str, str, str, str]:
        minus_flag: bool = self.__precise_time < 0
        temp_precise_time = abs(self.__precise_time)
        _hh, r_1 = divmod(temp_precise_time, 60*60)
        _mm, r_2 = divmod(r_1, 60)
        _ss, r_3 = divmod(r_2, 1)
        _sub_sec = round(r_3*sub_sec_multiplier)
        
        # Handle sub-second overflow
        if _sub_sec >= sub_sec_multiplier:
            _ss += _sub_sec // sub_sec_multiplier
            _sub_sec = _sub_sec % sub_sec_multiplier
            
            # Handle seconds overflow
            if _ss >= 60:
                _mm += _ss // 60
                _ss = _ss % 60
                
                # Handle minutes overflow
                if _mm >= 60:
                    _hh += _mm // 60
                    _mm = _mm % 60
        
        output_minus_flag = '' if not minus_flag else '-'
        output_hh = f'{output_minus_flag}{int(_hh):02d}'
        outpur_mm = f'{int(_mm):02d}'
        output_ss = f'{int(_ss):02d}'
        output_ff = f'{_sub_sec:{sub_sec_format}}'

        output_full_str = f'{output_hh}:{outpur_mm}:{output_ss}{frame_seperator}{output_ff}'

        return output_full_str, output_hh, outpur_mm, output_ss, output_ff

    def _convert_to_output_srt(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(sub_sec_multiplier=1000,
                                                          frame_seperator=',',
                                                          sub_sec_format='03d')

        if output_part > 4:
            logger.warning(
                'No such part, will return the last part of timecode')
            return output_strs[-1]

        return output_strs[output_part]
    ##

    def _convert_to_output_dlp(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(sub_sec_multiplier=250,
                                                          frame_seperator=':',
                                                          sub_sec_format='03d')

        if output_part > 4:
            logger.warning(
                'No such part, will return the last part of timecode')
            return output_strs[-1]

        return output_strs[output_part]

    def _convert_to_output_ffmpeg(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(sub_sec_multiplier=100,
                                                          frame_seperator='.',
                                                          sub_sec_format='02d')

        if output_part > 4:
            logger.warning(
                'No such part, will return the last part of timecode')
            return output_strs[-1]

        return output_strs[output_part]

    def _convert_to_output_fcpx(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logger.warning(
                '_convert_to_output_fcpx: This timecode type has only one part.')
        output_fcpx_denominator='' if float(self.__precise_time).is_integer() else self.__precise_time.denominator
        return f'{self.__precise_time.numerator}{output_fcpx_denominator}s'

    def _convert_to_output_frame(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logger.warning(
                'This timecode type [frame] has only one part.')
        return str(round(self.__precise_time * self.__fps))

    def _convert_to_output_time(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logger.warning(
                'This timecode type [time] has only one part.')
        output_time = round(float(self.__precise_time), 5)
        return str(output_time)

    def timecode_output(self, dest_type: TimecodeType = 'auto', output_part: int = 0) -> str:
        """Convert timecode to specified format and return as string.

        Args:
            dest_type: Target timecode format. Use 'auto' to output in current format.
                Available formats: 'smpte', 'srt', 'dlp', 'ffmpeg', 'fcpx', 'frame', 'time'.
                Defaults to 'auto'.
            output_part: For multi-part formats (SMPTE, SRT, DLP, FFMPEG), specify which
                part to return. 0 returns the complete timecode string, 1-4 return individual
                parts (hours, minutes, seconds, frames/subseconds). Defaults to 0.

        Returns:
            str: The formatted timecode string

        Raises:
            AttributeError: If dest_type is not a valid timecode format

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> tc.timecode_output('srt')
            '01:00:00,000'
            >>> tc.timecode_output('ffmpeg')
            '01:00:00.00'
            >>> tc.timecode_output('frame')
            '86400'
            >>> tc.timecode_output('smpte', output_part=1)  # Get hours only
            '01'

        Note:
            - For 'auto', outputs in the current timecode type
            - Falls back to SMPTE format if dest_type is invalid
        """
        if dest_type == 'auto':
            func = getattr(self, f'_convert_to_output_{self.__type}')
        else:
            func = getattr(self, f'_convert_to_output_{dest_type}')
        if func:
            return func(output_part)
        else:
            logger.warning(
                f'CANNOT find such destination type [{dest_type}], will return SMPTE type')
            func = getattr(self, '_convert_to_output_smpte', None)
            return func(output_part)

    def set_fps(self, dest_fps: float, rounding: bool = True) -> 'DfttTimecode':
        """Change the frame rate of the timecode.

        Args:
            dest_fps: Target frame rate in frames per second (0.01-999.99)
            rounding: If True, rounds the internal timestamp to the nearest frame
                at the new frame rate. If False, preserves exact timestamp.
                Defaults to True.

        Returns:
            DfttTimecode: Self reference for method chaining

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> tc.set_fps(30)
            >>> print(tc.fps)
            30.0
            >>> print(tc)  # Same time, different frame count
            01:00:00:00

        Note:
            This method modifies the object in place and returns self for chaining.
        """
        self.__fps = dest_fps
        self.__nominal_fps = ceil(self.__fps)
        if rounding:
            self.__precise_time = round(
                self.__precise_time * self.__fps) / self.__fps
        else:
            pass
        return self

    def set_type(self, dest_type: TimecodeType = 'smpte', rounding: bool = True) -> 'DfttTimecode':
        """Change the internal timecode format type.

        Args:
            dest_type: Target timecode format type. Available formats:
                'smpte', 'srt', 'dlp', 'ffmpeg', 'fcpx', 'frame', 'time'.
                Defaults to 'smpte'.
            rounding: If True, rounds the timestamp to match the precision of the
                new format. If False, preserves exact timestamp. Defaults to True.

        Returns:
            DfttTimecode: Self reference for method chaining

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> tc.set_type('srt')
            >>> print(tc.type)
            'srt'
            >>> print(tc)
            01:00:00,000

        Note:
            - This changes the internal type, affecting :meth:`__str__` output
            - Rounding adjusts precision to match format (e.g., SRT has millisecond precision)
            - Invalid types are ignored with a warning
        """
        if dest_type in ('smpte', 'srt', 'dlp', 'ffmpeg', 'fcpx', 'frame', 'time'):
            self.__type = dest_type
        else:
            logger.warning(f'No such type [{dest_type}], will remain current type.')
        if rounding:
            temp_str = self.timecode_output(dest_type)
            temp_timecode_object = DfttTimecode(
                temp_str, dest_type, self.__fps, self.__drop_frame, self.__strict)
            self.__precise_time = temp_timecode_object.__precise_time
        else:
            pass
        return self

    def set_strict(self, strict: bool = True) -> 'DfttTimecode':
        """Change the 24-hour strict mode setting.

        Args:
            strict: If True, enables 24-hour wraparound (timecodes cycle within 0-24 hours).
                If False, allows timecodes beyond 24 hours. Defaults to True.

        Returns:
            DfttTimecode: Self reference for method chaining

        Examples:
            >>> tc = DfttTimecode('25:00:00:00', fps=24, strict=False)
            >>> print(tc)
            25:00:00:00
            >>> tc.set_strict(True)
            >>> print(tc)
            01:00:00:00

        Note:
            Changing strict mode recalculates the internal timestamp with the new mode.
        """
        if strict == self.__strict:
            pass
        else:
            temp_timecode_object = DfttTimecode(self.__precise_time, 'time', self.__fps, self.__drop_frame,
                                                strict)
            self.__precise_time = temp_timecode_object.__precise_time
            self.__strict = strict
        return self

    def get_audio_sample_count(self, sample_rate: int) -> int:
        """Calculate the number of audio samples at the given sample rate.

        Converts the timecode to audio sample count for audio synchronization.
        Uses high-precision rational arithmetic to avoid rounding errors.

        Args:
            sample_rate: Audio sample rate in Hz (e.g., 44100, 48000, 96000)

        Returns:
            int: The number of audio samples (floored to nearest integer)

        Examples:
            >>> tc = DfttTimecode('00:00:01:00', fps=24)
            >>> tc.get_audio_sample_count(48000)
            48000
            >>> tc = DfttTimecode('00:00:00:01', fps=24)
            >>> tc.get_audio_sample_count(48000)  # 1 frame at 24fps
            2000

        Note:
            Uses floor division to ensure sample count doesn't exceed the timecode position.
        """
        numerator,denominator=self.__precise_time.as_integer_ratio()
        return floor(numerator * sample_rate/denominator)

    def __repr__(self) -> str:
        """Return detailed string representation of the timecode object.

        Returns:
            str: Detailed representation including timecode, type, fps, and mode flags

        Example:
            >>> tc = DfttTimecode('01:00:00:00', fps=24, drop_frame=False)
            >>> repr(tc)
            '<DfttTimecode>(Timecode:01:00:00:00, Type:smpte,FPS:24.00 NDF, Strict)'
        """
        drop_frame_flag = 'DF' if self.__drop_frame else 'NDF'
        strict_flag = 'Strict' if self.__strict else 'Non-Strict'
        return f'<DfttTimecode>(Timecode:{self.timecode_output(self.__type)}, Type:{self.__type},FPS:{float(self.__fps):.02f} {drop_frame_flag}, {strict_flag})'

    def __str__(self) -> str:
        """Return timecode as formatted string in current type.

        Returns:
            str: Timecode string in the current format type

        Example:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> str(tc)
            '01:00:00:00'
        """
        return self.timecode_output()

    def __add__(self, other: Union['DfttTimecode', int, float, Fraction]) -> 'DfttTimecode':
        """Add timecode with another timecode, frame count, or timestamp.

        Args:
            other: Value to add. Can be:
                - DfttTimecode: Adds timestamps (must have same fps and drop_frame)
                - int: Treats as frame count to add
                - float: Treats as seconds to add
                - Fraction: Treats as precise seconds to add

        Returns:
            DfttTimecode: New timecode object with the sum

        Raises:
            DFTTTimecodeOperatorError: If fps or drop_frame don't match between timecodes,
                or if other is an unsupported type

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> result = tc + 100  # Add 100 frames
            >>> print(result)
            01:00:04:04
            >>> result = tc + 3.5  # Add 3.5 seconds
            >>> print(result)
            01:00:03:12
            >>> tc2 = DfttTimecode('00:10:00:00', fps=24)
            >>> result = tc + tc2
            >>> print(result)
            01:10:00:00

        Note:
            - Result inherits the format type of the left operand
            - If either operand has strict=True, result will have strict=True
        """
        temp_sum = self.__precise_time
        if isinstance(other, DfttTimecode):
            if self.__fps == other.__fps and self.__drop_frame == other.__drop_frame:
                temp_sum = self.__precise_time + other.__precise_time
                self.__strict = self.__strict or other.__strict
            else:  # 帧率不同不允许相加，报错
                logger.error(
                    'Timecode addition requires exact same FPS.')
                raise DFTTTimecodeOperatorError
        elif isinstance(other, int):  # 帧
            temp_sum = self.__precise_time + (other / self.__fps)
        elif isinstance(other, float):  # 时间
            temp_sum = self.__precise_time + other
        elif isinstance(other, Fraction):  # 时间
            temp_sum = self.__precise_time + other
        else:
            logger.error(f'Undefined addition with [{type(other)}].')
            raise DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            temp_sum, 'time', self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __radd__(self, other: Union[int, float, Fraction]) -> 'DfttTimecode':
        """Reflected addition (called when left operand doesn't support +).

        Implements commutative property: other + timecode == timecode + other

        Args:
            other: Value to add (int, float, or Fraction)

        Returns:
            DfttTimecode: New timecode object with the sum

        Example:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> result = 100 + tc  # Same as tc + 100
            >>> print(result)
            01:00:04:04
        """
        return self.__add__(other)

    def __sub__(self, other: Union['DfttTimecode', int, float, Fraction]) -> 'DfttTimecode':
        """Subtract timecode, frame count, or timestamp from this timecode.

        Args:
            other: Value to subtract. Can be:
                - DfttTimecode: Subtracts timestamps (must have same fps and drop_frame)
                - int: Treats as frame count to subtract
                - float: Treats as seconds to subtract
                - Fraction: Treats as precise seconds to subtract

        Returns:
            DfttTimecode: New timecode object with the difference

        Raises:
            DFTTTimecodeOperatorError: If fps or drop_frame don't match between timecodes,
                or if other is an unsupported type

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24)
            >>> result = tc - 100  # Subtract 100 frames
            >>> print(result)
            00:59:55:20
            >>> result = tc - 3.5  # Subtract 3.5 seconds
            >>> print(result)
            00:59:56:12

        Note:
            Result can be negative, which will be displayed with a leading minus sign.
        """
        diff = self.__precise_time
        if isinstance(other, DfttTimecode):
            if self.__fps == other.__fps and self.__drop_frame == other.__drop_frame:
                diff = self.__precise_time - other.__precise_time
                self.__strict = self.__strict or other.__strict
            else:
                logger.error(
                    'Timecode subtraction requires exact same FPS.')
                raise DFTTTimecodeOperatorError
        elif isinstance(other, int):  # 帧
            diff = self.__precise_time - other / self.__fps
        elif isinstance(other, float):  # 时间
            diff = self.__precise_time - other
        elif isinstance(other, Fraction):  # 时间
            diff = self.__precise_time - other
        else:
            logger.error(f'Undefined subtraction with [{type(other)}].')
            raise DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            diff, 'time', self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __rsub__(self, other):  # 运算符重载，减法，同理，int是帧，float是时间
        diff = self.__precise_time
        if isinstance(other, int):  # 帧
            diff = other / self.__fps - self.__precise_time
        elif isinstance(other, float):  # 秒
            diff = other - self.__precise_time
        elif isinstance(other, Fraction):  # 时间
            diff = other - self.__precise_time
        else:
            logger.error(f'Undefined subtraction with [{type(other)}].')
            raise DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            diff, 'time', self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __mul__(self, other: Union[int, float, Fraction]) -> 'DfttTimecode':
        """Multiply timecode by a numeric factor.

        Args:
            other: Multiplication factor (int, float, or Fraction)

        Returns:
            DfttTimecode: New timecode with timestamp multiplied by factor

        Raises:
            DFTTTimecodeOperatorError: If attempting to multiply two timecodes or
                if other is an unsupported type

        Examples:
            >>> tc = DfttTimecode('00:00:10:00', fps=24)
            >>> result = tc * 2  # Double the timecode
            >>> print(result)
            00:00:20:00
            >>> result = tc * 0.5  # Half the timecode
            >>> print(result)
            00:00:05:00

        Note:
            Multiplying two timecode objects together is not allowed and will raise an error.
        """
        prod = self.__precise_time
        if isinstance(other, DfttTimecode):
            logger.error(
                'Timecode CANNOT multiply with another Timecode.')
            raise DFTTTimecodeOperatorError
        elif isinstance(other, int):
            prod = self.__precise_time * other
        elif isinstance(other, float):
            prod = self.__precise_time * other
        elif isinstance(other, Fraction):
            prod = self.__precise_time * other
        else:
            logger.error(f'Undefined multiplication with [{type(other)}].')
            raise DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            prod, 'time', self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __rmul__(self, other: Union[int, float, Fraction]) -> 'DfttTimecode':
        """Reflected multiplication (implements commutative property).

        Args:
            other: Multiplication factor (int, float, or Fraction)

        Returns:
            DfttTimecode: New timecode with timestamp multiplied by factor

        Example:
            >>> tc = DfttTimecode('00:00:10:00', fps=24)
            >>> result = 2 * tc  # Same as tc * 2
            >>> print(result)
            00:00:20:00
        """
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float, Fraction]) -> 'DfttTimecode':
        """Divide timecode by a numeric factor.

        Args:
            other: Division factor (int, float, or Fraction)

        Returns:
            DfttTimecode: New timecode with timestamp divided by factor

        Raises:
            DFTTTimecodeOperatorError: If attempting to divide timecodes or
                if other is an unsupported type

        Examples:
            >>> tc = DfttTimecode('00:00:10:00', fps=24)
            >>> result = tc / 2  # Half the timecode
            >>> print(result)
            00:00:05:00

        Note:
            Dividing two timecode objects is not allowed and will raise an error.
        """
        quo_time = self.__precise_time  # quo_time是商（时间戳）
        if isinstance(other, DfttTimecode):
            logger.error(
                'Timecode CANNOT be devided by another Timecode.')
            raise DFTTTimecodeOperatorError
        elif isinstance(other, int):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        elif isinstance(other, float):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        elif isinstance(other, Fraction):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        else:
            logger.error(f'Undefined division with [{type(other)}].')
            raise DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            quo_time, 'time', self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __rtruediv__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, Fraction):
            logger.error(
                'Number CANNOT be devided by a Timecode.')
            raise DFTTTimecodeOperatorError
        else:
            logger.error(f'Undefined division with [{type(other)}].')
            raise DFTTTimecodeOperatorError

    def __eq__(self, other: Union['DfttTimecode', int, float, Fraction]) -> bool:
        """Check equality with another timecode or numeric value.

        Args:
            other: Value to compare. Can be:
                - DfttTimecode: Compares timestamps (must have same fps)
                - int: Compares as frame count
                - float: Compares as seconds
                - Fraction: Compares as precise seconds

        Returns:
            bool: True if values are equal (within 5 decimal places), False otherwise

        Raises:
            DFTTTimecodeOperatorError: If comparing timecodes with different fps
            DFTTTimecodeTypeError: If other is an unsupported type

        Examples:
            >>> tc1 = DfttTimecode('01:00:00:00', fps=24)
            >>> tc2 = DfttTimecode('01:00:00:00', fps=24)
            >>> tc1 == tc2
            True
            >>> tc1 == 86400  # Compare with frame count
            True
            >>> tc1 == 3600.0  # Compare with seconds
            True
        """
        if isinstance(other, DfttTimecode):  # 与另一个Timecode对象比较 比双方的时间戳 精确到5位小数
            if self.fps != other.fps:
                raise DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) == round(other.__precise_time, 5)
        elif isinstance(other, int):  # 与int比较 默认int为帧号 比较当前timecode对象的帧号是否与其一致
            return int(self.timecode_output('frame')) == other
        elif isinstance(other, float):  # 与float比较 默认float为时间戳 比较当前timecode对象的时间戳是否与其一致 精确到5位小数
            return float(round(self.__precise_time, 5)) == round(other, 5)
        # 与Fraction比较 默认Fraction为时间戳 比较当前timecode对象的时间戳是否与其一致 精确到5位小数
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) == round(other, 5)
        else:
            logger.error(f'CANNOT compare with data type [{type(other)}].')
            raise DFTTTimecodeTypeError

    def __ne__(self, other: Union['DfttTimecode', int, float, Fraction]) -> bool:
        """Check inequality with another timecode or numeric value.

        Args:
            other: Value to compare (DfttTimecode, int, float, or Fraction)

        Returns:
            bool: True if values are not equal, False otherwise

        Example:
            >>> tc1 = DfttTimecode('01:00:00:00', fps=24)
            >>> tc2 = DfttTimecode('01:00:00:01', fps=24)
            >>> tc1 != tc2
            True
        """
        return not self.__eq__(other)

    def __lt__(self, other: Union['DfttTimecode', int, float, Fraction]) -> bool:
        """Check if this timecode is less than another value.

        Args:
            other: Value to compare. Can be:
                - DfttTimecode: Compares timestamps (must have same fps)
                - int: Compares as frame count
                - float: Compares as seconds
                - Fraction: Compares as precise seconds

        Returns:
            bool: True if this timecode is less than other, False otherwise

        Raises:
            DFTTTimecodeOperatorError: If comparing timecodes with different fps
            DFTTTimecodeTypeError: If other is an unsupported type

        Example:
            >>> tc1 = DfttTimecode('01:00:00:00', fps=24)
            >>> tc2 = DfttTimecode('02:00:00:00', fps=24)
            >>> tc1 < tc2
            True
        """
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) < round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output('frame')) < other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) < round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) < round(other, 5)
        else:
            logger.error(f'CANNOT compare with data type [{type(other)}].')
            raise DFTTTimecodeTypeError

    def __le__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) <= round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output('frame')) <= other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) <= round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) <= round(other, 5)
        else:
            logger.error(f'CANNOT compare with data type [{type(other)}].')
            raise DFTTTimecodeTypeError

    def __gt__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) > round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output('frame')) > other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) > round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) > round(other, 5)
        else:
            logger.error(f'CANNOT compare with data type [{type(other)}].')
            raise DFTTTimecodeTypeError

    def __ge__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) >= round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output('frame')) >= other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) >= round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) >= round(other, 5)
        else:
            logger.error(f'CANNOT compare with data type [{type(other)}].')
            raise DFTTTimecodeTypeError

    def __neg__(self) -> 'DfttTimecode':
        """Return the negation of this timecode.

        Returns:
            DfttTimecode: New timecode with negated timestamp

        Note:
            In strict mode, negative timecodes wrap around within 24 hours.
            For example, -01:00:00:00 becomes 23:00:00:00 in strict mode.

        Examples:
            >>> tc = DfttTimecode('01:00:00:00', fps=24, strict=False)
            >>> neg_tc = -tc
            >>> print(neg_tc)
            -01:00:00:00
            >>> tc_strict = DfttTimecode('01:00:00:00', fps=24, strict=True)
            >>> neg_tc_strict = -tc_strict
            >>> print(neg_tc_strict)
            23:00:00:00
        """
        temp_object = DfttTimecode(-self.__precise_time, 'time',
                                   self.__fps, self.__drop_frame, self.__strict)
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __float__(self) -> float:
        """Convert timecode to float (seconds).

        Returns:
            float: The timestamp in seconds

        Example:
            >>> tc = DfttTimecode('00:00:10:00', fps=24)
            >>> float(tc)
            10.0
        """
        return self.timestamp

    def __int__(self) -> int:
        """Convert timecode to integer (frame count).

        Returns:
            int: The frame count

        Example:
            >>> tc = DfttTimecode('00:00:01:00', fps=24)
            >>> int(tc)
            24
        """
        return self.framecount
