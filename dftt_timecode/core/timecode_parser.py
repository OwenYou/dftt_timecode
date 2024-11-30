import logging
from fractions import Fraction
from functools import singledispatchmethod
from math import ceil

import dftt_timecode.error as dftt_errors
import dftt_timecode.pattern as tc_patterns


class TimecodeParser:
    tc_type = "time"
    fps = 24.0  # 帧率
    nominal_fps = 24  # 名义帧率（无小数,进一法取整）
    drop_frame = False  # 是否丢帧Dropframe（True为丢帧，False为不丢帧）
    strict = True  # 严格模式，默认为真，在该模式下不允许超出24或小于0的时码，将自动平移至0-24范围内，例如-1小时即为23小时，25小时即为1小时
    precise_time = Fraction(0)  # 精准时间戳，是所有时码类对象的工作基础

    @singledispatchmethod
    def parse_timecode(self, timecode_value, timecode_type, fps, drop_frame, strict):
        raise NotImplementedError(f"Cannot process type {type(timecode_value)}")

    @parse_timecode.register  # 若传入的TC值为字符串，则调用此函数
    def _(
        self,
        timecode_value: str,
        timecode_type="auto",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_value[0] == "-":  # 判断首位是否为负，并为flag赋值
            minus_flag = True
        else:
            minus_flag = False
        self.fps = fps
        # 读入帧率取整为名义帧率便于后续计算（包括判断时码是否合法，DF/NDF逻辑等) 用进一法是因为要判断ff值是否大于fps-1
        self.nominal_fps = ceil(fps)
        self.drop_frame = drop_frame
        self.strict = strict
        if (
            round(self.fps, 2) % 29.97 != 0
            and round(self.fps, 2) % 23.98 != 0
            and self.drop_frame
        ):  # 判断丢帧状态与时码输入是否匹配 不匹配则强制转换
            self.drop_frame = False
            logging.info(
                "Timecode.__init__.str: This FPS is NOT Drop-Framable, force drop_frame to False"
            )
        else:
            pass
        if timecode_type == "auto":  # 自动判断类型逻辑
            if tc_patterns.SMPTE_NDF_REGEX.match(
                timecode_value
            ):  # SMPTE NDF 强制DF为False
                timecode_type = "smpte"
                if self.drop_frame:
                    # 判断丢帧状态与帧率是否匹配 不匹配则强制转换
                    if (
                        round(self.fps, 2) % 29.97 == 0
                        or round(self.fps, 2) % 23.98 == 0
                    ):
                        self.drop_frame = True
                    else:
                        self.drop_frame = False
                        logging.info(
                            "Timecode.__init__.str.auto: This FPS is NOT Drop-Framable, force drop_frame to False"
                        )
                else:
                    self.drop_frame = False
            elif tc_patterns.SMPTE_DF_REGEX.match(timecode_value):
                timecode_type = "smpte"
                # 判断丢帧状态与帧率是否匹配 不匹配则强制转换
                if round(self.fps, 2) % 29.97 == 0 or round(self.fps, 2) % 23.98 == 0:
                    self.drop_frame = True
                else:
                    self.drop_frame = False
                    logging.info(
                        "Timecode.__init__.str.auto: This FPS is NOT Drop-Framable, force drop_frame to False"
                    )
            elif tc_patterns.SRT_REGEX.match(timecode_value):
                timecode_type = "srt"
            elif tc_patterns.FFMPEG_REGEX.match(timecode_value):
                timecode_type = "ffmpeg"
            elif tc_patterns.FCPX_REGEX.match(timecode_value):
                timecode_type = "fcpx"
            elif tc_patterns.FRAME_REGEX.match(timecode_value):
                timecode_type = "frame"
            elif tc_patterns.TIME_REGEX.match(timecode_value):
                timecode_type = "time"
            else:
                pass
        else:
            pass  # 这里不用elif是因为auto类型也需要利用下面的部分进行操作
        if timecode_type == "smpte":  # smpte TC
            match = tc_patterns.SMPTE_REGEX.match(timecode_value)
            if match:  # 判断输入是否符合SMPTE类型
                pass
            else:
                logging.error(
                    "Timecode.__init__.smpte: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_list = [
                int(x) if x else 0 for x in match.groups()
            ]  # 正则取值
            hh = temp_timecode_list[0]
            mm = temp_timecode_list[1]
            ss = temp_timecode_list[2]
            ff = temp_timecode_list[3]
            if ff > self.nominal_fps - 1:  # 判断输入帧号在当前帧率下是否合法
                logging.error(
                    "Timecode.__init__.smpte: This timecode is illegal under given params, check your input!"
                )
                raise dftt_errors.DFTTTimecodeValueError
            else:
                pass
            if not self.drop_frame:  # 时码丢帧处理逻辑
                frame_index = ff + self.nominal_fps * (ss + mm * 60 + hh * 3600)
            else:
                drop_per_min = self.nominal_fps / 30 * 2
                # 检查是否有DF下不合法的帧号
                if mm % 10 != 0 and ss == 0 and ff in (0, drop_per_min - 1):
                    logging.error(
                        "Timecode.__init__.smpte: This timecode is illegal under given params, check your input!"
                    )
                    raise dftt_errors.DFTTTimecodeValueError
                else:
                    total_minutes = 60 * hh + mm
                    frame_index = (
                        (hh * 3600 + mm * 60 + ss) * self.nominal_fps
                        + ff
                        - (self.nominal_fps / 30)
                        * 2
                        * (
                            # 逢十分钟不丢帧 http://andrewduncan.net/timecodes/
                            total_minutes
                            - total_minutes // 10
                        )
                    )
            if self.strict:  # strict输入逻辑
                frame_index = (
                    frame_index % (self.fps * 86400)
                    if self.drop_frame
                    else frame_index % (self.nominal_fps * 86400)
                )  # 对于DF时码来说，严格处理取真实FPS的模，对于NDF时码，则取名义FPS的模
            else:
                pass
            if not minus_flag:
                pass
            else:
                frame_index = -frame_index
            self.precise_time = Fraction(frame_index / self.fps)  # 时间戳=帧号/帧率
        elif timecode_type == "srt":  # srt字幕
            match = tc_patterns.SRT_REGEX.match(
                timecode_value
            )  # 判断输入是否符合SRT类型
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.srt: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_list = [int(x) if x else 0 for x in match.groups()]
            # 由于SRT格式本身不存在帧率，将为SRT赋予默认帧率和丢帧状态
            logging.info(
                "Timecode.__init__.srt: SRT timecode framerate "
                + str(self.fps)
                + ", DF="
                + str(self.drop_frame)
                + " assigned"
            )
            hh = temp_timecode_list[0]
            mm = temp_timecode_list[1]
            ss = temp_timecode_list[2]
            sub_sec = temp_timecode_list[3]  # 取毫秒
            if not minus_flag:
                self.precise_time = Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 1000)
            else:
                self.precise_time = -(
                    Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 1000)
                )
            if self.strict:
                self.precise_time = self.precise_time % 86400
            else:
                pass
        elif timecode_type == "dlp":  # cinecanvas字幕
            match = tc_patterns.DLP_REGEX.match(timecode_value)
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.dlp: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_list = [int(x) if x else 0 for x in match.groups()]
            # 由于DLP不存在帧率，将为DLP赋予默认帧率和丢帧状态
            logging.info(
                "Timecode.__init__.dlp: DLP timecode framerate "
                + str(self.fps)
                + ", DF="
                + str(self.drop_frame)
                + " assigned"
            )
            hh = temp_timecode_list[0]
            mm = temp_timecode_list[1]
            ss = temp_timecode_list[2]
            sub_sec = temp_timecode_list[3]  # 取子帧戳 dlp每秒共250个子帧 即4ms一个
            # 详见https://interop-docs.cinepedia.com/Reference_Documents/CineCanvas(tm)_RevC.pdf 第17页 “TimeIn”部分
            if not minus_flag:
                self.precise_time = Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 250)
            else:
                self.precise_time = -Fraction(hh * 3600 + mm * 60 + ss + sub_sec / 250)
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        elif timecode_type == "ffmpeg":  # ffmpeg时间
            match = tc_patterns.FFMPEG_REGEX.match(timecode_value)
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.ffmpeg: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_list = [int(x) if x else 0 for x in match.groups()]
            hh = temp_timecode_list[0]
            mm = temp_timecode_list[1]
            ss = temp_timecode_list[2]
            sub_sec = temp_timecode_list[3]
            if not minus_flag:
                self.precise_time = Fraction(
                    hh * 3600 + mm * 60 + ss + float(f"0.{sub_sec}")
                )
            else:
                self.precise_time = -Fraction(
                    hh * 3600 + mm * 60 + ss + float(f"0.{sub_sec}")
                )
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        elif timecode_type == "fcpx":  # fcpx xml时间戳
            match = tc_patterns.FCPX_REGEX.match(timecode_value)
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.fcpx: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_list = [int(x) if x else 0 for x in match.groups()]
            print(temp_timecode_list[0])
            if not minus_flag:
                self.precise_time = Fraction(
                    temp_timecode_list[0], temp_timecode_list[1]
                )
            else:
                self.precise_time = -Fraction(
                    temp_timecode_list[0], temp_timecode_list[1]
                )
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        elif timecode_type == "frame":  # 帧计数
            match = tc_patterns.FRAME_REGEX.match(timecode_value)
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.frame: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_frame_index = int(match.group(1))
            if (
                self.strict
            ):  # 严格模式，对于丢帧时码而言 用实际FPS运算，对于不丢帧时码而言，使用名义FPS运算
                temp_frame_index = (
                    temp_frame_index % (self.fps * 86400)
                    if self.drop_frame
                    else temp_frame_index % (self.nominal_fps * 86400)
                )
            else:
                pass
            self.precise_time = Fraction(
                temp_frame_index / self.fps
            )  # 转换为内部精准时间戳
        elif timecode_type == "time":  # 内部时间戳生成
            match = tc_patterns.TIME_REGEX.match(timecode_value)
            if match:
                pass
            else:
                logging.error(
                    "Timecode.__init__.time: Timecode type DONOT match input value! Check input."
                )
                raise dftt_errors.DFTTTimecodeTypeError
            self.tc_type = timecode_type
            temp_timecode_value = match.group(1)
            self.precise_time = Fraction(
                temp_timecode_value
            )  # 内部时间戳直接等于输入值
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.str: Unknown type or type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeValueError
        instance_success_log = (
            "Timecode.__init__.str: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)

    @parse_timecode.register  # 输入为Fraction类分数，此时认为输入是时间戳，若不是，则会报错
    def _(
        self,
        timecode_value: Fraction,
        timecode_type="time",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_type in ("time", "auto"):
            self.tc_type = "time"
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            self.precise_time = timecode_value  # 内部时间戳直接等于输入值
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.Fraction: Timecode type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeTypeError
        instance_success_log = (
            "Timecode.__init__.Fraction: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)

    @parse_timecode.register
    def _(
        self,
        timecode_value: int,
        timecode_type="frame",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_type in ("frame", "auto"):
            self.tc_type = "frame"
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            temp_frame_index = timecode_value
            if self.strict:
                temp_frame_index = (
                    temp_frame_index % (self.fps * 86400)
                    if self.drop_frame
                    else temp_frame_index % (self.nominal_fps * 86400)
                )
            else:
                pass
            self.precise_time = Fraction(temp_frame_index / self.fps)
        elif timecode_type == "time":
            self.tc_type = "time"
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            self.precise_time = timecode_value  # 内部时间戳直接等于输入值
            if self.strict:  # strict逻辑 对于非帧相关值（时间戳） 直接取模
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.int: Timecode type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeTypeError
        instance_success_log = (
            "Timecode.__init__.int: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)

    @parse_timecode.register
    def _(
        self,
        timecode_value: float,
        timecode_type="time",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_type in ("time", "auto"):
            self.tc_type = "time"
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            self.precise_time = Fraction(timecode_value)  # 内部时间戳直接等于输入值
            if self.strict:
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.float: Timecode type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeTypeError
        instance_success_log = (
            "Timecode.__init__.float: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)

    @parse_timecode.register
    def _(
        self,
        timecode_value: tuple,
        timecode_type="time",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_type in ("time", "auto"):
            self.tc_type = "time"
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            self.precise_time = Fraction(
                int(timecode_value[0]), int(timecode_value[1])
            )  # 将tuple输入视为分数
            if self.strict:
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.tuple: Timecode type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeTypeError
        instance_success_log = (
            "Timecode.__init__.tuple: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)

    @parse_timecode.register
    def _(
        self,
        timecode_value: list,
        timecode_type="time",
        fps=24.0,
        drop_frame=False,
        strict=True,
    ):
        if timecode_type in ("time", "auto"):
            self.tc_type = timecode_type
            self.fps = fps
            self.nominal_fps = ceil(fps)
            self.drop_frame = drop_frame
            self.strict = strict
            self.precise_time = Fraction(
                int(timecode_value[0]), int(timecode_value[1])
            )  # 将list输入视为分数
            if self.strict:
                self.precise_time = self.precise_time % 86400
            else:
                pass
        else:
            logging.error(
                "Timecode.__init__.list: Timecode type DONOT match input value! Check input."
            )
            raise dftt_errors.DFTTTimecodeTypeError
        instance_success_log = (
            "Timecode.__init__.list: Timecode instance, type="
            + str(self.tc_type)
            + ", fps="
            + str(self.fps)
            + ", dropframe="
            + str(self.drop_frame)
            + ", strict="
            + str(self.strict)
        )
        logging.debug(instance_success_log)
