# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0b1] - 2025-10-24

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
