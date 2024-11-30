import logging
from fractions import Fraction
from math import ceil, floor

from dftt_timecode.core.timecode_parser import TimecodeParser
import dftt_timecode.error as dftt_errors


class DfttTimecode:
    __type = "time"
    __fps = 24.0  # 帧率
    __nominal_fps = 24  # 名义帧率（无小数,进一法取整）
    __drop_frame = False  # 是否丢帧Dropframe（True为丢帧，False为不丢帧）
    __strict = True  # 严格模式，默认为真，在该模式下不允许超出24或小于0的时码，将自动平移至0-24范围内，例如-1小时即为23小时，25小时即为1小时
    __precise_time = Fraction(0)  # 精准时间戳，是所有时码类对象的工作基础

    def __new__(
        cls,
        timecode_value,
        timecode_type="auto",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if isinstance(timecode_value, DfttTimecode):
            return timecode_value
        else:
            return super(DfttTimecode, cls).__new__(cls)

    def __init__(
        self,
        timecode_value,
        timecode_type="auto",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):  # 构造函数
        if timecode_value is None:
            timecode_value = 0
        tc = TimecodeParser()
        tc.parse_timecode(timecode_value, timecode_type, fps, drop_frame, strict)
        self.__type = tc.tc_type
        self.__fps = tc.fps
        self.__nominal_fps = tc.nominal_fps
        self.__drop_frame = tc.drop_frame
        self.__strict = tc.strict
        self.__precise_time = tc.precise_time

    @property
    def type(self) -> str:
        return self.__type

    @property
    def fps(self):
        return self.__fps

    @property
    def is_drop_frame(self) -> bool:
        return self.__drop_frame

    @property
    def is_strict(self) -> bool:
        return self.__strict

    @property
    def framecount(self) -> int:
        return int(self._convert_to_output_frame())

    @property
    def timestamp(self) -> float:
        return float(self._convert_to_output_time())

    @property
    def precise_timestamp(self):
        return self.__precise_time

    def _convert_to_output_smpte(self, output_part=0) -> str:
        minus_flag = False
        frame_index = round(
            self.__precise_time * self.__fps
        )  # 从内部时间戳计算得帧计数
        if frame_index < 0:  # 负值时，打上flag，并翻转负号
            minus_flag = True
            frame_index = -frame_index

        # 计算framecount用于输出smpte时码个部分值
        if not self.__drop_frame:  # 不丢帧
            # 对于不丢帧时码而言 framecount 为帧计数
            _nominal_framecount = frame_index
        else:  # 丢帧
            drop_per_min = (
                self.__nominal_fps / 30 * 2
            )  # 提前计算每分钟丢帧数量 简化后续计算
            df_framecount_10min = self.__nominal_fps * 600 - 9 * drop_per_min

            d, m = divmod(frame_index, df_framecount_10min)
            drop_frame_frame_number = (
                frame_index
                + drop_per_min * 9 * d
                + drop_per_min
                * (
                    # 剩余小于十分钟部分计算丢了多少帧，补偿
                    ((m - drop_per_min) // (self.__nominal_fps * 60 - drop_per_min))
                    if m > 2
                    else 0
                )
            )

            _nominal_framecount = drop_frame_frame_number

        def _convert_framecount_to_smpte_parts(frame_count: int, fps: int) -> tuple:
            hour, r_1 = divmod(frame_count, 60 * 60 * fps)
            minute, r_2 = divmod(r_1, 60 * fps)
            second, frame = divmod(r_2, fps)
            return int(hour), int(minute), int(second), round(frame)

        output_hh, output_mm, output_ss, output_ff = _convert_framecount_to_smpte_parts(
            int(_nominal_framecount), self.__nominal_fps
        )

        output_ff_format = "02d" if self.__fps < 100 else "03d"
        output_minus_flag = "" if not minus_flag else "-"
        output_strs = (
            f"{output_minus_flag}{output_hh:02d}",
            f"{output_mm:02d}",
            f"{output_ss:02d}",
            f"{output_ff:{output_ff_format}}",
        )

        if output_part > len(output_strs):
            logging.warning(
                "Timecode._convert_to_output_smpte: No such part, will return the last part of timecode"
            )
            return output_strs[-1]

        # 输出完整时码字符串
        if output_part == 0:
            main_part = ":".join(output_strs[:3])
            # 丢帧时码的帧号前应为分号
            separator = ";" if self.__drop_frame else ":"
            output_str = f"{main_part}{separator}{output_strs[3]}"
            return output_str

        elif 1 <= output_part <= len(output_strs):
            return output_strs[output_part - 1]

        else:
            raise IndexError(
                "Timecode._convert_to_output_smpte: Negtive output_part is not allowed"
            )

    def _convert_precise_time_to_parts(
        self, sub_sec_multiplier: int, frame_seperator: str, sub_sec_format: str
    ) -> tuple[str, str, str, str, str]:
        minus_flag: bool = self.__precise_time < 0
        temp_precise_time = abs(self.__precise_time)
        _hh, r_1 = divmod(temp_precise_time, 60 * 60)
        _mm, r_2 = divmod(r_1, 60)
        _ss, r_3 = divmod(r_2, 1)
        _sub_sec = round(r_3 * sub_sec_multiplier)
        output_minus_flag = "" if not minus_flag else "-"
        output_hh = f"{output_minus_flag}{_hh:02d}"
        outpur_mm = f"{_mm:02d}"
        output_ss = f"{_ss:02d}"
        output_ff = f"{_sub_sec:{sub_sec_format}}"

        output_full_str = (
            f"{output_hh}:{outpur_mm}:{output_ss}{frame_seperator}{output_ff}"
        )

        return output_full_str, output_hh, outpur_mm, output_ss, output_ff

    def _convert_to_output_srt(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(
            sub_sec_multiplier=1000, frame_seperator=",", sub_sec_format="03d"
        )

        if output_part > 4:
            logging.warning(
                "Timecode._convert_to_output_srt: No such part, will return the last part of timecode"
            )
            return output_strs[-1]

        return output_strs[output_part]

    ##

    def _convert_to_output_dlp(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(
            sub_sec_multiplier=250, frame_seperator=":", sub_sec_format="03d"
        )

        if output_part > 4:
            logging.warning(
                "Timecode._convert_to_output_srt: No such part, will return the last part of timecode"
            )
            return output_strs[-1]

        return output_strs[output_part]

    def _convert_to_output_ffmpeg(self, output_part=0) -> str:
        output_strs = self._convert_precise_time_to_parts(
            sub_sec_multiplier=100, frame_seperator=".", sub_sec_format="02d"
        )

        if output_part > 4:
            logging.warning(
                "Timecode._convert_to_output_srt: No such part, will return the last part of timecode"
            )
            return output_strs[-1]

        return output_strs[output_part]

    def _convert_to_output_fcpx(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logging.warning(
                "_convert_to_output_fcpx: This timecode type has only one part."
            )
        output_fcpx_denominator = (
            ""
            if float(self.__precise_time).is_integer()
            else self.__precise_time.denominator
        )
        return f"{self.__precise_time.numerator}{output_fcpx_denominator}s"

    def _convert_to_output_frame(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logging.warning(
                "Timecode._convert_to_output_frame: This timecode type has only one part."
            )
        return str(round(self.__precise_time * self.__fps))

    def _convert_to_output_time(self, output_part=0) -> str:
        if output_part == 0:
            pass
        else:
            logging.warning(
                "Timecode._convert_to_output_time: This timecode type has only one part."
            )
        output_time = round(float(self.__precise_time), 5)
        return str(output_time)

    def timecode_output(self, dest_type="auto", output_part=0):
        if dest_type == "auto":
            func = getattr(self, f"_convert_to_output_{self.__type}")
        else:
            func = getattr(self, f"_convert_to_output_{dest_type}")
        if func:
            return func(output_part)
        else:
            logging.warning(
                "Timecode.timecode_output: CANNOT find such destination type, will return SMPTE type"
            )
            func = getattr(self, "_convert_to_output_smpte")
            return func(output_part)

    def set_fps(self, dest_fps, rounding=True) -> "DfttTimecode":
        self.__fps = dest_fps
        self.__nominal_fps = ceil(self.__fps)
        if rounding:
            self.__precise_time = round(self.__precise_time * self.__fps) / self.__fps
        else:
            pass
        return self

    def set_type(self, dest_type="smpte", rounding=True) -> "DfttTimecode":
        if dest_type in ("smpte", "srt", "dlp", "ffmpeg", "fcpx", "frame", "time"):
            self.__type = dest_type
        else:
            logging.warning("No such type, will remain current type.")
        if rounding:
            temp_str = self.timecode_output(dest_type)
            temp_timecode_object = DfttTimecode(
                temp_str,
                dest_type,
                self.__fps,
                self.__drop_frame,
                self.__strict,
            )
            self.__precise_time = temp_timecode_object.__precise_time
        else:
            pass
        return self

    def set_strict(self, strict=True) -> "DfttTimecode":
        if strict == self.__strict:
            pass
        else:
            temp_timecode_object = DfttTimecode(
                self.__precise_time,
                "time",
                self.__fps,
                self.__drop_frame,
                strict,
            )
            self.__precise_time = temp_timecode_object.__precise_time
            self.__strict = strict
        return self

    def get_audio_sample_count(self, sample_rate: int) -> int:
        numerator, denominator = self.__precise_time.as_integer_ratio()
        return floor(numerator * sample_rate / denominator)

    def __repr__(self):
        drop_frame_flag = "DF" if self.__drop_frame else "NDF"
        strict_flag = "Strict" if self.__strict else "Non-Strict"
        return f"<DfttTimecode>(Timecode:{self.timecode_output(self.__type)}, Type:{self.__type},FPS:{float(self.__fps):.02f} {drop_frame_flag}, {strict_flag})"

    def __str__(self):
        return self.timecode_output()

    def __add__(self, other):  # 运算符重载，加号，加int则认为是帧，加float则认为是时间
        temp_sum = self.__precise_time
        if isinstance(other, DfttTimecode):
            if self.__fps == other.__fps and self.__drop_frame == other.is_drop_frame:
                temp_sum = self.__precise_time + other.__precise_time
                self.__strict = self.__strict or other.__strict
            else:  # 帧率不同不允许相加，报错
                logging.error(
                    "Timecode.__add__: Timecode addition requires exact same FPS."
                )
                raise dftt_errors.DFTTTimecodeOperatorError
        elif isinstance(other, int):  # 帧
            temp_sum = self.__precise_time + (other / self.__fps)
        elif isinstance(other, float):  # 时间
            temp_sum = self.__precise_time + other
        elif isinstance(other, Fraction):  # 时间
            temp_sum = self.__precise_time + other
        else:
            logging.error("Timecode.__add__: Undefined addition.")
            raise dftt_errors.DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            temp_sum, "time", self.__fps, self.__drop_frame, self.__strict
        )
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __radd__(self, other):  # 加法交换律
        return self.__add__(other)

    def __sub__(self, other):  # 运算符重载，减法，同理，int是帧，float是时间
        diff = self.__precise_time
        if isinstance(other, DfttTimecode):
            if self.__fps == other.__fps and self.__drop_frame == other.is_drop_frame:
                diff = self.__precise_time - other.__precise_time
                self.__strict = self.__strict or other.__strict
            else:
                logging.error(
                    "Timecode.__sub__: Timecode subtraction requires exact same FPS."
                )
                raise dftt_errors.DFTTTimecodeOperatorError
        elif isinstance(other, int):  # 帧
            diff = self.__precise_time - other / self.__fps
        elif isinstance(other, float):  # 时间
            diff = self.__precise_time - other
        elif isinstance(other, Fraction):  # 时间
            diff = self.__precise_time - other
        else:
            logging.log(30, "Timecode.__sub__: Undefined subtraction.")
            raise dftt_errors.DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            diff, "time", self.__fps, self.__drop_frame, self.__strict
        )
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
            logging.error("Timecode.__rsub__: Undefined subtraction.")
            raise dftt_errors.DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            diff, "time", self.__fps, self.__drop_frame, self.__strict
        )
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __mul__(self, other):  # 运算符重载，乘法，int和float都是倍数
        prod = self.__precise_time
        if isinstance(other, DfttTimecode):
            logging.error(
                "Timecode.__mul__: Timecode CANNOT multiply with another Timecode."
            )
            raise dftt_errors.DFTTTimecodeOperatorError
        elif isinstance(other, int):
            prod = self.__precise_time * other
        elif isinstance(other, float):
            prod = self.__precise_time * other
        elif isinstance(other, Fraction):
            prod = self.__precise_time * other
        else:
            logging.error("Timecode.__mul__: Undefined multiplication.")
            raise dftt_errors.DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            prod, "time", self.__fps, self.__drop_frame, self.__strict
        )
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __rmul__(self, other):  # 乘法交换律
        return self.__mul__(other)

    def __truediv__(self, other):
        quo_time = self.__precise_time  # quo_time是商（时间戳）
        if isinstance(other, DfttTimecode):
            logging.error(
                "Timecode.__truediv__: Timecode CANNOT be devided by another Timecode."
            )
            raise dftt_errors.DFTTTimecodeOperatorError
        elif isinstance(other, int):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        elif isinstance(other, float):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        elif isinstance(other, Fraction):  # timecode与数相除，得到结果是timecode
            quo_time = self.__precise_time / other
        else:
            logging.error("Timecode.__truediv__: Undefined division.")
            raise dftt_errors.DFTTTimecodeOperatorError
        temp_object = DfttTimecode(
            quo_time, "time", self.__fps, self.__drop_frame, self.__strict
        )
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __rtruediv__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, Fraction)
        ):
            logging.error(
                "Timecode.__rtruediv__: Number CANNOT be devided by a Timecode."
            )
            raise dftt_errors.DFTTTimecodeOperatorError
        else:
            logging.error("Timecode.__rtruediv__: Undefined division.")
            raise dftt_errors.DFTTTimecodeOperatorError

    def __eq__(self, other):  # 判断相等
        if isinstance(
            other, DfttTimecode
        ):  # 与另一个Timecode对象比较 比双方的时间戳 精确到5位小数
            if self.fps != other.fps:
                raise dftt_errors.DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) == round(other.__precise_time, 5)
        elif isinstance(
            other, int
        ):  # 与int比较 默认int为帧号 比较当前timecode对象的帧号是否与其一致
            return int(self.timecode_output("frame")) == other
        elif isinstance(
            other, float
        ):  # 与float比较 默认float为时间戳 比较当前timecode对象的时间戳是否与其一致 精确到5位小数
            return float(round(self.__precise_time, 5)) == round(other, 5)
        # 与Fraction比较 默认Fraction为时间戳 比较当前timecode对象的时间戳是否与其一致 精确到5位小数
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) == round(other, 5)
        else:
            logging.error("CANNOT compare with such data type.")
            raise dftt_errors.DFTTTimecodeTypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise dftt_errors.DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) < round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output("frame")) < other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) < round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) < round(other, 5)
        else:
            logging.error("CANNOT compare with such data type.")
            raise dftt_errors.DFTTTimecodeTypeError

    def __le__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise dftt_errors.DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) <= round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output("frame")) <= other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) <= round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) <= round(other, 5)
        else:
            logging.error("CANNOT compare with such data type.")
            raise dftt_errors.DFTTTimecodeTypeError

    def __gt__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise dftt_errors.DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) > round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output("frame")) > other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) > round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) > round(other, 5)
        else:
            logging.error("CANNOT compare with such data type.")
            raise dftt_errors.DFTTTimecodeTypeError

    def __ge__(self, other):  # 详见__eq__
        if isinstance(other, DfttTimecode):
            if self.fps != other.fps:
                raise dftt_errors.DFTTTimecodeOperatorError
            else:
                return round(self.__precise_time, 5) >= round(other.__precise_time, 5)
        elif isinstance(other, int):
            return int(self.timecode_output("frame")) >= other
        elif isinstance(other, float):
            return float(round(self.__precise_time, 5)) >= round(other, 5)
        elif isinstance(other, Fraction):
            return round(self.__precise_time, 5) >= round(other, 5)
        else:
            logging.error("CANNOT compare with such data type.")
            raise dftt_errors.DFTTTimecodeTypeError

    def __neg__(self):
        # 取负操作 返回时间戳取负的Timecode对象（strict规则照常应用 例如01:00:00:00 strict的对象 取负后为23:00:00:00）
        temp_object = DfttTimecode(
            -self.__precise_time,
            "time",
            self.__fps,
            self.__drop_frame,
            self.__strict,
        )
        temp_object.set_type(self.type, rounding=False)
        return temp_object

    def __float__(self):
        return self.timestamp

    def __int__(self):
        return self.framecount

    def __deepcopy__(self, memo):
        return DfttTimecode(
            self.timestamp, self.type, self.fps, self.is_drop_frame, self.is_strict
        )
