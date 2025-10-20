# DFTT Timecode

[![pypi](https://img.shields.io/badge/pypi-0.0.14-brightgreen)](https://pypi.org/project/dftt-timecode/)
[![python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![GitHub license](https://img.shields.io/badge/license-LGPL2.1-green)](https://github.com/OwenYou/dftt_timecode/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://owenyou.github.io/dftt_timecode/)

A high-precision Python timecode library designed for film and TV production.

为影视行业设计的高精度Python时码库。

## Introduction | 简介

DFTT Timecode is a professional-grade timecode library for film and television post-production workflows. It provides frame-accurate calculations with support for multiple industry-standard formats, high frame rates, and drop-frame compensation.

DFTT Timecode是一个专业级的时码库，专为影视后期制作工作流设计。它提供帧精确的计算，支持多种行业标准格式、高帧率和丢帧补偿。

**DFTT** stands for Department of Film and TV Technology of Beijing Film Academy.

**DFTT**是北京电影学院影视技术系（Department of Film and TV Technology）的缩写。

### Key Features | 主要特性

- **Multiple Format Support** - SMPTE, SRT, DLP (Cine Canvas), FFMPEG, FCPX, frame count, and timestamps

  **多格式支持** - SMPTE、SRT、DLP（Cine Canvas）、FFMPEG、FCPX、帧计数和时间戳

- **High Frame Rate** - Supports 0.01 to 999.99 fps

  **高帧率** - 支持0.01至999.99 fps

- **Drop-Frame Accurate** - Strict SMPTE drop-frame/non-drop-frame compliance

  **丢帧精确** - 严格遵循SMPTE丢帧/非丢帧标准

- **High Precision** - Uses `fractions.Fraction` internally for lossless calculations

  **高精度** - 内部使用`fractions.Fraction`进行无损计算

- **Rich Operators** - Full arithmetic (+, -, *, /) and comparison (==, !=, <, >, <=, >=) support

  **丰富的运算符** - 完整的算术和比较运算支持

- **Strict Mode** - Optional 24-hour wrapping for broadcast workflows

  **严格模式** - 可选的24小时循环模式，适用于广播工作流

## Installation | 安装

```bash
pip install dftt_timecode
```

**Requirements:** Python 3.11 or higher

**要求：** Python 3.11或更高版本

## Quick Start | 快速入门

### Basic Usage | 基本使用

```python
from dftt_timecode import DfttTimecode

# Create timecode from SMPTE format
tc = DfttTimecode('01:00:00:00', 'auto', fps=24)
print(tc)  # <DfttTimecode>(Timecode:01:00:00:00, Type:smpte, FPS:24.00 NDF, Strict)

# Access timecode properties
print(tc.framecount)   # 86400
print(tc.timestamp)    # 3600.0
print(tc.fps)          # 24

# Convert to different formats
print(tc.timecode_output('smpte'))   # 01:00:00:00
print(tc.timecode_output('srt'))     # 01:00:00,000
print(tc.timecode_output('ffmpeg'))  # 01:00:00.00
```

### Arithmetic Operations | 运算操作

```python
from dftt_timecode import DfttTimecode

a = DfttTimecode('01:00:00:00', fps=24)
b = DfttTimecode('00:30:00:00', fps=24)

# Timecode arithmetic
print(a + b)   # 01:30:00:00
print(a - b)   # 00:30:00:00
print(a * 2)   # 02:00:00:00
print(a / 2)   # 00:30:00:00

# Comparison
print(a > b)   # True
print(a == b)  # False

# Add frames (int) or seconds (float)
print(a + 24)    # Adds 24 frames
print(a + 1.0)   # Adds 1 second
```

### Drop-Frame Timecode | 丢帧时码

```python
from dftt_timecode import DfttTimecode

# Drop-frame timecode for 29.97 fps
df_tc = DfttTimecode('01:00:00;00', fps=29.97, drop_frame=True)
print(df_tc)  # Automatically detects drop-frame from semicolon separator

# Non-drop-frame
ndf_tc = DfttTimecode('01:00:00:00', fps=29.97, drop_frame=False)
```

### Format Conversion | 格式转换

```python
from dftt_timecode import DfttTimecode

tc = DfttTimecode('1000f', fps=24)  # Create from frame count

# Convert to different formats
tc.set_type('smpte')
print(tc.timecode_output())  # 00:00:41:16

tc.set_type('srt')
print(tc.timecode_output())  # 00:00:41,667

# Change frame rate
tc.set_fps(25, rounding=True)
print(tc.timecode_output('smpte'))  # 00:00:40:00
```

### Using Convenience Aliases | 使用便捷别名

```python
# Shorter aliases for quick coding
from dftt_timecode import dtc, dtr

tc = dtc('01:00:00:00', fps=24)  # dtc = DfttTimecode
print(tc.framecount)  # 86400
```

## Documentation | 文档

For comprehensive documentation including detailed API reference, advanced usage, and examples:

完整文档包括详细的API参考、高级用法和示例：

**📖 [View Full Documentation on GitHub Pages](https://owenyou.github.io/dftt_timecode/)**

### Documentation Contents | 文档内容

- **API Reference** - Complete class and method documentation

  **API参考** - 完整的类和方法文档

- **Advanced Usage** - TimeRange operations, precision handling, format conversion

  **高级用法** - TimeRange操作、精度处理、格式转换

- **Examples** - Real-world usage patterns and best practices

  **示例** - 实际应用模式和最佳实践

- **Format Specifications** - Detailed format descriptions and validation rules

  **格式规范** - 详细的格式描述和验证规则

## TimeRange Support | 时间范围支持

The library includes `DfttTimeRange` for working with time intervals:

库中包含用于处理时间间隔的`DfttTimeRange`：

```python
from dftt_timecode import DfttTimeRange

# Create a time range
tr = DfttTimeRange(
    start='01:00:00:00',
    end='02:00:00:00',
    fps=24
)

print(tr.duration)  # Duration timecode
print(tr.framecount)  # Total frames in range

# TimeRange operations
tr1 = DfttTimeRange('01:00:00:00', '02:00:00:00', fps=24)
tr2 = DfttTimeRange('01:30:00:00', '02:30:00:00', fps=24)

intersection = tr1.intersection(tr2)  # Overlapping portion
union = tr1.union(tr2)  # Combined range
```

See the [full documentation](https://owenyou.github.io/dftt_timecode/) for complete TimeRange API reference.

查看[完整文档](https://owenyou.github.io/dftt_timecode/)了解完整的TimeRange API参考。

## License | 许可证

This project is licensed under the LGPL 2.1 License - see the [LICENSE](LICENSE) file for details.

本项目采用LGPL 2.1许可证 - 详见[LICENSE](LICENSE)文件。

## Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交Pull Request。

## Links | 链接

- **PyPI:** https://pypi.org/project/dftt-timecode/
- **Documentation:** https://owenyou.github.io/dftt_timecode/
- **Source Code:** https://github.com/OwenYou/dftt_timecode
- **Issue Tracker:** https://github.com/OwenYou/dftt_timecode/issues
