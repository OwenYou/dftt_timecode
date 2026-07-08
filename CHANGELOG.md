# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for timecodes whose hours field exceeds 99 hours. Colon-separated formats (SMPTE, SRT, FFMPEG, DLP) now accept an unbounded hours field (still zero-padded to at least 2 digits), so non-strict timecodes such as `100:00:00:00` are parsed correctly. This lifts the previous -99–99 hour range limit; single-digit unpadded hours (`1:00:00:00`) remain invalid

  支持小时字段超过 99 小时的时码。冒号分隔格式（SMPTE、SRT、FFMPEG、DLP）现在接受无上限的小时字段（仍需补零至至少两位），因此 `100:00:00:00` 等非严格模式时码可被正确解析。此前 -99–99 小时的范围限制已被取消；未补零的单位数小时（`1:00:00:00`）仍视为无效

## [1.0.0] - 2026-05-12

### Summary

First stable release. The library graduates from beta with the breaking changes accumulated during the `1.0.0b*` series finalized. Downstream code that worked against `1.0.0b4` should require no further changes.

首个正式版本。库从测试版毕业，`1.0.0b*` 系列累积的破坏性变更在此版本定稿。已适配 `1.0.0b4` 的下游代码无需进一步修改。

### Fixed

- Initialization failures in `DfttTimecode` no longer leave behind a half-built object that silently behaves like a "value-0 timecode at 24 fps". The five class-level state defaults (`__fps`, `__nominal_fps`, `__drop_frame`, `__strict`, `__precise_time`) that masked missing instance attributes have been removed; any access to state on a partial instance now raises `AttributeError`

  `DfttTimecode` 初始化失败时不再遗留一个表现为「24fps 下零值时码」的半构造对象。原本掩盖未赋值实例属性的五个类级别默认值（`__fps`、`__nominal_fps`、`__drop_frame`、`__strict`、`__precise_time`）已被移除；对半构造实例的状态访问现在会抛出 `AttributeError`

### Removed

- **Breaking:** Remove `configure_logging()` and `get_logger()` from the public API (`dftt_timecode.configure_logging`, `dftt_timecode.get_logger`)

  **破坏性变更：** 从公开 API 中移除 `configure_logging()` 和 `get_logger()`

- **Breaking:** Remove the `dftt_timecode.logging_config` module. Logging is now configured directly inside core modules using a standard `NullHandler`, following the recommended library logging convention. Downstream code should configure logging via the standard `logging` module

  **破坏性变更：** 移除 `dftt_timecode.logging_config` 模块。日志现在在核心模块内部直接配置，并按照库日志最佳实践添加 `NullHandler`。下游代码应使用标准 `logging` 模块自行配置日志

- **Breaking:** Remove the `DfttTimecode(existing_tc)` passthrough constructor introduced in 0.0.10. Passing an existing `DfttTimecode` to the constructor now raises `DFTTTimecodeTypeError` like any other unsupported input type. The previous behavior returned the same instance unchanged (`DfttTimecode(tc) is tc`), which created an aliasing footgun when the result was subsequently passed to mutators like `set_fps()`. Callers that want to reuse an instance should pass it directly; callers that want an independent copy should construct from a primitive representation such as `precise_timestamp`, `framecount`, or a string form

  **破坏性变更：** 移除 0.0.10 引入的 `DfttTimecode(existing_tc)` 透传构造行为。现在向构造器传入已有的 `DfttTimecode` 会和其它不支持的输入类型一样抛出 `DFTTTimecodeTypeError`。原行为返回的是同一个实例（`DfttTimecode(tc) is tc`），后续若调用 `set_fps()` 等就地修改方法会出现别名陷阱。需要复用实例的调用方请直接使用原对象；需要独立副本的调用方请改用 `precise_timestamp`、`framecount` 或字符串等基本表示重新构造

- **Breaking (latent):** Remove five class-level state attributes on `DfttTimecode` (`__fps`, `__nominal_fps`, `__drop_frame`, `__strict`, `__precise_time`). These were never part of the documented API but were observable via `vars(DfttTimecode)` / class-attribute inspection. See the corresponding Fixed entry above for the user-visible behavior change

  **破坏性变更（隐性）：** 移除 `DfttTimecode` 上的五个类级别状态属性（`__fps`、`__nominal_fps`、`__drop_frame`、`__strict`、`__precise_time`）。它们从未作为文档化 API 公开，但可通过 `vars(DfttTimecode)` 等方式观测到。用户可见的行为变化见上方 Fixed 条目

### Changed

- **Breaking:** `DfttTimecode.timecode_output()` no longer silently falls back to SMPTE when a conversion method raises an unexpected exception. Only the defensive `AttributeError` guard remains; other errors now propagate to the caller

  **破坏性变更：** `DfttTimecode.timecode_output()` 在转换方法抛出意外异常时，不再静默回退到 SMPTE 格式。仅保留对 `AttributeError` 的防御性回退，其它异常会正常抛给调用方

- **Breaking:** Narrow the exception wrapping in `DfttTimeRange.offset()`, `DfttTimeRange.extend()`, and `DfttTimeRange.__contains__()`. Previously a broad `except Exception` re-raised everything as `DFTTTimeRangeMethodError` / `DFTTTimeRangeTypeError`; now only `DFTTError` raised during internal `DfttTimecode` construction is wrapped, and other exception types propagate unchanged

  **破坏性变更：** 收窄 `DfttTimeRange.offset()`、`DfttTimeRange.extend()` 和 `DfttTimeRange.__contains__()` 中的异常包装范围。之前用宽泛的 `except Exception` 将所有异常重新包装；现在只包装内部构造 `DfttTimecode` 时抛出的 `DFTTError`，其它类型异常按原类型透传

- All `DFTTError` subclasses raised across `DfttTimecode` and `DfttTimeRange` now carry descriptive messages (`raise DFTTTimecodeOperatorError("...")`). Previously many sites raised the bare exception class with no message and emitted a separate `logger.error(...)` line, so `str(exc)` / `exc.args` were empty

  所有在 `DfttTimecode` 和 `DfttTimeRange` 中抛出的 `DFTTError` 子类现在都附带描述性消息。之前多处只 `raise` 异常类本身（无消息）并额外打一条 `logger.error(...)` 日志，导致 `str(exc)` / `exc.args` 为空

- Stop logging an `ERROR` record immediately before raising a `DFTTError`. The exception itself is now the single source of truth; callers using log capture for error visibility will see fewer records

  在抛出 `DFTTError` 前不再额外记录一条 `ERROR` 日志。异常本身作为唯一的错误信息来源；依赖日志捕获错误信息的调用方将看到更少的日志记录

- **Breaking:** The base `DfttTimecode.__init__` overload now raises `DFTTTimecodeTypeError` for unsupported input types (previously raised bare `TypeError`). Callers using `try / except DFTTError:` will now catch this case alongside other library errors

  **破坏性变更：** `DfttTimecode.__init__` 的 dispatch 兜底分支在收到不支持的输入类型时改为抛出 `DFTTTimecodeTypeError`（原为裸 `TypeError`）。使用 `try / except DFTTError:` 的调用方现在会一并捕获到该情况

## [1.0.0b3]

### Fixed

- Fix Python 3.14 compatibility issue in `move_frame()` method where `Fraction()` constructor with two arguments failed due to stricter type requirements

  修复 Python 3.14 兼容性问题，`move_frame()` 方法中 `Fraction()` 构造函数因更严格的类型要求而失败

- Fix precision loss issues in timecode initialization methods (`__init_smpte()`, `__init_frame()`) by using `Fraction()` division instead of float division

  修复时码初始化方法中的精度损失问题，使用 `Fraction()` 除法替代浮点数除法

- Fix FCPX format output to correctly handle integer timestamps, avoiding large numerator values when the result is a whole number

  修复 FCPX 格式输出，正确处理整数时间戳，避免结果为整数时出现大分子值

### Added

- Add `move_frame()` and `move_time()` methods to DfttTimecode class for moving timecode by specified frames or time duration

  为 DfttTimecode 类添加 `move_frame()` 和 `move_time()` 方法，用于按指定帧数或时间段移动时码

- Add comprehensive unit tests (32 tests) for `move_frame()` and `move_time()` methods

  为 `move_frame()` 和 `move_time()` 方法添加全面的单元测试（32 个测试）

  - Frame movement tests: forward/backward movement, zero movement, large movements (86400 frames)

    帧移动测试：正向/反向移动、零移动、大规模移动（86400 帧）

  - Time movement tests: float/int/Fraction input support, various time movements

    时间移动测试：浮点数/整数/分数输入支持、各种时间移动

  - Strict mode tests: 24-hour cycling behavior verification

    严格模式测试：24 小时循环行为验证

  - Different frame rates: 24, 30, 60, 119.88 fps

    不同帧率：24、30、60、119.88 fps

  - Drop-frame timecode support tests

    丢帧时码支持测试

  - Method chaining and input validation tests

    方法链和输入验证测试

  - Equivalence test between `move_frame()` and `move_time()`

    `move_frame()` 和 `move_time()` 的等价性测试

### Changed

- Improved internal timestamp precision across the entire codebase by consistently using `Fraction()` arithmetic

  通过始终使用 `Fraction()` 算术运算，提高整个代码库的内部时间戳精度

## [1.0.0b2]
### Fixed
- Fix bug for fcpx output format
  修复 fcpx 输出格式的错误

## [1.0.0b1]

### Summary

First beta release! The library has reached feature completeness and API stability for its core functionality. All major features are implemented, tested, and documented. This beta release is ready for production testing and feedback.

### Added

- Comprehensive internationalization (i18n) support with Chinese translations

  完整的国际化支持，包含中文翻译

- Language switcher in documentation

  文档语言切换器

- Enhanced documentation with auto-generated changelog integration

  增强文档，自动集成 CHANGELOG.md

### Changed

- API is now considered stable for 1.0.0 release

  API 现在被视为稳定版本，准备发布 1.0.0

- Updated development status from Pre-Alpha to Beta

  开发状态从预览版更新为测试版

### Core Features (Stable)

- Multiple timecode format support: SMPTE (DF/NDF), SRT, FFMPEG, FCPX, DLP, frame count, timestamps

  多种时码格式支持

- High frame rate support (0.01-999.99 fps)

  高帧率支持

- High-precision calculations using Fraction for lossless accuracy

  使用 Fraction 进行高精度计算

- Full arithmetic operators (+, -, *, /) and comparison operators (==, !=, <, >, <=, >=)

  完整的算术和比较运算符

- DfttTimeRange class for time interval operations

  时间范围操作类

- Comprehensive test coverage with pytest

  完整的测试覆盖

- Sphinx-based documentation with API reference

  基于 Sphinx 的文档和 API 参考

- Automated CI/CD for documentation and PyPI publishing

  自动化 CI/CD 用于文档和 PyPI 发布

## [0.0.15a2] - Pre-Alpha

### Fixed

- Fix several error string missing user input logging during format

  修复遗漏的错误信息格式化 [#26](https://github.com/OwenYou/dftt_timecode/issues/26)

## [0.0.15a1] - Pre-Alpha

### Added

- Add `DfttTimecodeInitializationError` exception class

  增加 `DfttTimecodeInitializationError`

- Add GitHub Action to automatically upload releases to PyPI

  使用 GitHub Action 自动打包上传 PyPI

### Changed

- Modify drop frame logic to adapt to more frame rates

  修改丢帧逻辑适应更多帧率

- Refactor timecode type detection logic

  重构时码类型检测逻辑

- Refactor error handling during timecode initialization

  重构时码对象初始化时的错误处理

- Modify error messages to enhance readability

  修改报错信息，增强可读性

### Deprecated

- Completely remove `InstanceMethodDispatch`

  完全移除 `InstanceMethodDispatch`

### Fixed

- Fix millisecond overflow issue when converting certain timecodes from SMPTE to SRT [#19](https://github.com/OwenYou/dftt_timecode/issues/19)

  修复特定时码在SMPTE转SRT时毫秒会溢出的问题

## [0.0.14]

### Fixed

- Fix v0.0.13 import failure caused by missing dftt_timecode.core while packing

  修复v0.0.13打包后不包含core，导致库无法使用的问题

## [0.0.13]

### Added

- Add `get_audio_sample_count` method for correctly outputting the count of audio samples at TC timestamps [#9](https://github.com/OwenYou/dftt_timecode/issues/9)

  添加 `get_audio_sample_count` 方法用于正确输出TC时间戳下的音频采样数

### Changed

- Use f-string for string format output

  使用 `f-string` 处理字符串格式输出

- Refactor timecode output function to reduce code duplication

  重构时间码输出函数，减少代码重复

### Deprecated

- Use `functools.singledispatchmethod` instead of `dispatch.InstanceMethodDispatch`

  使用 `functools.singledispatchmethod` 代替 `dispatch.InstanceMethodDispatch`

## [0.0.12]

### Fixed

- Fix DLP pattern error causing DLP ticks in range [50-99] and [150-199] to not be matched. This bug caused errors when using strings like `'00:00:27:183'` to initialize a DLP timecode object

  修复DLP正则表达式错误导致范围在50-99、150-199的DLP tick不能被匹配的问题

## [0.0.11]

### Added

- Add `__str__` method to return timecode value for DfttTimecode object

  添加 `__str__` 方法，返回DfttTimecode对象的时间码值

- Add unit tests for DfttTimecode using pytest

  添加DfttTimecode单元测试（使用pytest）

### Changed

- Add 23.98/23.976 FPS to drop frame detection conditions

  对丢帧的检测条件添加有关23.98/23.976的判定

- `+` and `-` operators perform an OR operation on the strict property of two DfttTimecode objects being added/subtracted

  `+` `-` 运算符对相加的两个DfttTimecode对象的strict属性进行或运算

- Comparison operators (`==`, `>`, `>=`, etc.) now validate that both DfttTimecode objects have the same frame rate before comparison, throwing an exception if frame rates differ

  比较运算符在对两个DfttTimecode对象进行比较时会先判定帧率，若帧率不同则抛出异常

- `print(self)` now outputs a formatted timecode string

  `print(self)` 将会输出基于类型的时间码字符串

### Fixed

- Fix issue in `timecode_output(self, dest_type, output_part)` where `output_part = 3` would incorrectly return minute data

  修复 `timecode_output` 中 `output_part = 3` 时错误返回分钟数据的问题

## [0.0.10]

### Added

- Add support for using a DfttTimecode object to initialize a new DfttTimecode object

  使用DfttTimecode对象初始化新DfttTimecode对象

- Add `float()` and `int()` class methods for DfttTimecode class

  添加DfttTimecode类的float和int方法

- Add `precise_timestamp` attribute for DfttTimecode class

  添加DfttTimecode类的precise_timestamp属性

### Changed

- DfttTimecode operators now raise errors when encountering undefined circumstances or illegal operations

  DfttTimecode运算符在未定义/非法操作时将会报错

- Update comparison rules for DfttTimecode operators

  修改DfttTimecode运算符的大小比较规则

- When creating a timecode object using SMPTE NDF format string, if `drop_frame` is forced to `True`, the resulting object will be SMPTE DF format timecode

  使用SMPTE NDF格式字符串新建时码类对象时，若强制drop_frame为True，则新建得到的对象为SMPTE DF格式时码

## [0.0.9]

Initial public release.
